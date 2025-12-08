import asyncio
import json
import logging
import time
import urllib.parse
import weakref
from typing import Dict, Any

from fastapi import Request
from datetime import datetime, timezone
from fastapi.datastructures import Headers
from jose import jwt
from starlette.types import ASGIApp, Receive, Scope, Send
from elasticsearch import AsyncElasticsearch

from settings import settings



class LogLevelEnum:
    level_mapping = {
        2: "Info",
        3: "Warning",
        4: "Warning",
        5: "Error"
    }


class ElasticsearchLoggerMiddleware:
    def __init__(self, app: ASGIApp, config: dict) -> None:
        """
        Initializes an Elasticsearch Logger Middleware for FastAPI.

        Args:
            app (ASGIApp): The FastAPI ASGI application.
            config (dict): Configuration settings for Elasticsearch logging.
                {
                    'url': str,          # Elasticsearch server URL
                    'user': str,         # Elasticsearch API user
                    'password': str      # Elasticsearch API password
                    'index': str,        # Elasticsearch index name
                    'environment': str,  # Environment identifier for logs
                    'limit': bool,       # Limit Elasticsearch payload array and string lenght
                    'debug': bool        # When True logs aren't sent to Elasticsearch
                }
        """
        elastic_config = config
        elastic_user = config.get('user')
        elastic_password = config.get('password')
        basic_auth = (elastic_user, elastic_password) if elastic_user and elastic_password else None
        self.elasticsearch_client = AsyncElasticsearch([elastic_config.get('url')], basic_auth=basic_auth)
        self.index = elastic_config.get('index')
        self.limit = elastic_config.get('limit', False)
        self.environment = elastic_config.get('environment', 'Development')
        self.debug = elastic_config.get('debug', False)
        self.app = app

        # 📊 Para tracking de tareas en background
        self.background_tasks = weakref.WeakSet()
        # 📈 Configurar logger para debugging
        self.logger = logging.getLogger(__name__)

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope.get('type') == 'http' and not self.debug:
            request = Request(scope)

            async def intercept_send(response):
                nonlocal log_data

                if response['type'] == 'http.response.start':
                    # Request part - configurar headers y status
                    request_headers = dict(request.headers) if 'headers' in request.keys() else None
                    request_query_parameters = dict(request.query_params) if len(
                        request.query_params._list) > 0 else None

                    response_headers = dict(
                        Headers(raw=response.get('headers'))) if 'headers' in response.keys() else None
                    log_data["status_code"] = response['status']
                    log_data["level"] = LogLevelEnum.level_mapping.get(int(str(response['status'])[0]))
                    log_data["request"]["headers"] = request_headers
                    log_data["request"]["query_parameters"] = request_query_parameters
                    log_data["response"]["headers"] = response_headers

                    # Enviar response start
                    await send(response)

                elif response['type'] == 'http.response.body':
                    # Response body part
                    if not log_data.get("response"):
                        # Streaming response, no procesamos
                        await send(response)
                        return

                    # Finishes telemetry
                    end_time = time.time()
                    elapsed_time = end_time - start_time
                    log_data["elapsed_time"] = elapsed_time

                    # Procesar response body según content-type
                    if log_data["response"]["headers"].get('content-type') == 'application/json':
                        try:
                            response_body = json.loads(response.get('body'))
                            response_body = self.limit_array_length(response_body)
                            response_body = json.dumps(response_body,
                                                       ensure_ascii=False) if 'body' in response.keys() else None
                            log_data["response"]["body"] = response_body
                        except Exception as err:
                            log_data["response"]["body"] = str(response.get('body')) if 'body' in response.keys() else None
                    elif log_data["response"]["headers"].get('content-type') == 'application/octet-stream':
                        log_data["response"]["body"] = str(response.get('body')) if 'body' in response.keys() else None
                    elif log_data["response"]["headers"].get('content-type') == 'x-www-form-urlencoded':
                        response_body = response.get('body').decode('utf-8') if 'body' in response.keys() else None
                        response_body = self.limit_string_length(response_body)
                        log_data["response"]["body"] = response_body
                    else:
                        log_data["response"]["body"] = str(response.get('body')) if 'body' in response.keys() else None

                    # Extraer user_id del token si existe
                    if scope.get('headers', None):
                        headers = dict(Headers(scope=scope))
                        autorization_header = headers.get('authorization', None)
                        if autorization_header and 'bearer' in autorization_header.lower():
                            try:
                                token = autorization_header.split(' ')[1]
                                payload = jwt.decode(
                                    token, settings.SECRET_KEY, algorithms=['RS256']
                                )
                                log_data["user_id"] = payload['sub']
                            except Exception as e:
                                self.logger.debug(f"Error decodificando token: {e}")

                    # 🚀 Programar logging en background SIN BLOQUEAR
                    self._schedule_elasticsearch_log(log_data.copy())

                    # Enviar response body
                    await send(response)

                    # Limpiar log_data para próxima request
                    log_data["response"] = {}
                else:
                    # Otros tipos de mensajes ASGI
                    await send(response)

            log_data = {
                "@timestamp": datetime.now(tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%S"),
                "environment": self.environment,
                "method": request.method,
                "path": request.url.path,
                "request": {},
                "response": {}
            }
            # Starts telemetry
            start_time = time.time()

            async def intercept_receive():
                message = await receive()
                more_body = message.get("more_body", False)
                body = message.get("body", "")

                while more_body:
                    message = await receive()
                    body += message.get("body", b"")
                    more_body = message.get("more_body", False)

                message["body"] = body
                request_body = ''
                if len(message["body"]) > 0:
                    try:
                        request_body = json.loads(body.decode('utf-8'))
                        request_body = self.limit_string_length(request_body)
                        request_body = json.dumps(request_body, ensure_ascii=False) if len(
                            body.decode('utf-8')) > 0 else None
                    except Exception as error:
                        request_body = urllib.parse.unquote_plus(body.decode('ISO-8859-1'))
                        request_body = self.limit_string_length(request_body)
                log_data["request"]["body"] = request_body
                return message

            await self.app(scope, intercept_receive, intercept_send)
        else:
            await self.app(scope, receive, send)

    def _schedule_elasticsearch_log(self, log_data: Dict[str, Any]) -> None:
        """
        Programar el logging de Elasticsearch sin bloquear el flujo principal
        """
        task = asyncio.create_task(self._safe_log_to_elasticsearch(log_data))
        self.background_tasks.add(task)
        # Auto-cleanup cuando la tarea termina
        task.add_done_callback(self.background_tasks.discard)

    async def _safe_log_to_elasticsearch(self, log_data: Dict[str, Any]) -> None:
        """
        Wrapper seguro para logging que maneja errores sin afectar la aplicación
        """
        try:
            await self.log_to_elasticsearch(log_data)
            self.logger.debug(f"Log enviado exitosamente a Elasticsearch para {log_data.get('path', 'unknown')}")
        except Exception as e:
            # Log el error pero NO propagar la excepción
            self.logger.error(f"Error enviando log a Elasticsearch: {str(e)}")
            # Opcional: Enviar a un sistema de fallback (archivo, otra DB, etc.)
            await self._fallback_logging(log_data, str(e))

    async def log_to_elasticsearch(self, log_data: Dict[str, Any]) -> None:
        """
        Función asíncrona para enviar logs a Elasticsearch
        """
        try:
            # 🚀 Usar el cliente asíncrono
            await self.elasticsearch_client.index(index=self.index, body=log_data)
        except Exception as e:
            # Re-lanzar para que _safe_log_to_elasticsearch maneje el error
            raise e

    async def _fallback_logging(self, log_data: Dict[str, Any], error_msg: str) -> None:
        """
        Sistema de fallback cuando Elasticsearch falla
        """
        try:
            # Ejemplo: escribir a archivo como fallback
            fallback_data = {
                "timestamp": datetime.now().isoformat(),
                "error": error_msg,
                "original_log": log_data
            }

            # Aquí podrías escribir a un archivo, enviar a otro servicio, etc.
            self.logger.warning(f"Fallback logging activado: {json.dumps(fallback_data)}")

            # Ejemplo: escribir a archivo asíncrono
            # import aiofiles
            # async with aiofiles.open('elasticsearch_fallback.log', 'a') as f:
            #     await f.write(json.dumps(fallback_data) + '\n')

        except Exception as fallback_error:
            self.logger.critical(f"Falló incluso el sistema de fallback: {fallback_error}")

    async def close(self) -> None:
        """
        Cerrar el cliente de Elasticsearch correctamente
        """
        if hasattr(self.elasticsearch_client, 'close'):
            await self.elasticsearch_client.close()

    def limit_string_length(self, data, max_lines=50):
        if not self.limit:
            return data
        if isinstance(data, dict):
            for key, value in data.items():
                data[key] = self.limit_string_length(value, max_lines)
        elif isinstance(data, list):
            for i in range(len(data)):
                data[i] = self.limit_string_length(data[i], max_lines)
        elif isinstance(data, str) and len(data.split('\n')) > max_lines:
            data_splitted = data.split('\n')[:max_lines]
            data_splitted.append(f' [...] value limited in {max_lines} lines')
            data = '\n'.join(data_splitted)
        elif isinstance(data, str) and len(data.split('/')) > max_lines:  # Base64 files
            data_splitted = data.split('/')[:max_lines]
            data_splitted.append(f' [...] value limited in {max_lines} lines')
            data = '/'.join(data_splitted)
        return data

    def limit_array_length(self, data, max_length=3):
        if not self.limit:
            return data
        if isinstance(data, dict):
            for key, value in data.items():
                data[key] = self.limit_array_length(value, max_length)
        elif isinstance(data, list) and len(data) > max_length:
            data = data[:max_length]
            data.append(f'[...] array limited in {max_length} objects')
        return data
