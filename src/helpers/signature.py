import hmac
import hashlib
import json
import time

from settings import settings


class GraphQLClient:
    def __init__(self):
        self.secret = settings.secret_graphql
        self.version = settings.version_graphql

    @staticmethod
    def canonicalize(body):
        if isinstance(body, dict):
            # Serialize the dictionary to a JSON string with sorted keys and no spaces
            return json.dumps(body, separators=(',', ':'), sort_keys=True)
        elif isinstance(body, str):
            return body
        else:
            return str(body)


    def generate_backend_api_signature(self, body):
        timestamp = int(time.time() * 1000)
        payload = f"{timestamp}.{self.canonicalize(body)}"
        digest = hmac.new(
            key=self.secret.encode(),
            msg=payload.encode(),
            digestmod=hashlib.sha256
        ).hexdigest()
        return f"t={timestamp}, v{self.version}={digest}"

    def get_signature_headers(self, graphql_query):
        """
        generates the headers required for the GraphQL API request
        """
        signature = self.generate_backend_api_signature(graphql_query)
        headers = {
            "Content-Type": "application/json; charset=utf-8",
            "signature": signature,
            'tenant-id': settings.tenant_id
        }
        return headers


# class Scripts:
#     def __init__(self, req, res):
#         self.req = req
#         self.res = res
#
#
#     def resolve_template_variables(self, string):
#         # Usa una regex para {{nombreVariable}}
#         VARIABLE_NAME_REGEX = r'{{([A-Za-z]\w+)}}'
#
#         def replacer(match):
#             key = match.group(1)
#             return self.bru.get_var(key) or self.bru.get_env_var(key)
#         return re.sub(VARIABLE_NAME_REGEX, replacer, string)
#
#     def sanitize_url(self):
#         url = self.resolve_template_variables(self.req.get_url())
#         def replacer(match):
#             key = match.group(1)
#             return self.bru.get_env_var('host3000') if key == '3' else self.bru.get_env_var('host4000')
#         return re.sub(r'localhost:([3,4])000', replacer, url)
#
#     def sanitize_body(self):
#         request_body = self.req.get_body()
#         if not (self.req.get_method().upper() == 'POST' and request_body):
#             return None
#         if isinstance(request_body, dict):
#             request_body = json.dumps(request_body)
#         resolved = self.resolve_template_variables(request_body)
#         def replacer(match):
#             key = match.group(1)
#             return 'https://' + (self.bru.get_env_var('host3000') if key == '3' else self.bru.get_env_var('host4000'))
#         cleaned = re.sub(r'http://localhost:([3,4])000', replacer, resolved)
#         return json.loads(cleaned)
#
#     def sanitize_headers(self):
#         headers_str = json.dumps(self.req.get_headers())
#         resolved = self.resolve_template_variables(headers_str)
#         return json.loads(resolved)
#
#     def request_sig_headers(self, url, method, headers, body):
#         base_url = self.bru.get_env_var('signatureUrl')
#         payload = {
#             "keyId": self.bru.get_env_var('clientKeyId'),
#             "base64Key": self.bru.get_env_var('clientPrivateKey'),
#             "request": {
#                 "url": url,
#                 "method": method,
#                 "headers": headers,
#                 "body": json.dumps(body)
#             }
#         }
#         response = requests.post(
#             base_url,
#             headers={"Content-Type": "application/json"},
#             json=payload
#         )
#         return response.json()
#
#     def set_headers(self, headers):
#         for key, value in headers.items():
#             self.req.set_header(key, value)
#
#     def add_signature_headers(self):
#         url = self.sanitize_url()
#         headers = self.sanitize_headers()
#         body = self.sanitize_body()
#         self.req.set_body(body)
#         signature_headers = self.request_sig_headers(
#             url,
#             self.req.get_method(),
#             headers,
#             body
#         )
#         self.set_headers(signature_headers)
#
#     def canonicalize(self, data):
#         # Reemplazo básico para json-canonicalize (¡ajusta si requieres RFC detallado!)
#         return json.dumps(data, sort_keys=True, separators=(',', ':'))
#
#     def generate_auth_api_signature(self, body):
#         version = self.bru.get_env_var('authApiSignatureVersion')
#         secret = self.bru.get_env_var('authApiSignatureSecret')
#         timestamp = int(__import__('time').time() * 1000)
#         payload = f"{timestamp}.{self.canonicalize(body)}"
#         digest = hmac.new(
#             key=secret.encode(),
#             msg=payload.encode(),
#             digestmod=hashlib.sha256
#         ).hexdigest()
#         return f"t={timestamp}, v{version}={digest}"
#
#     def generate_backend_api_signature(self, body):
#         version = 1
#         secret = 'iyIgCprjb9uL8wFckR+pLEkJWMB7FJhgkvqhTQR/964='
#         timestamp = int(__import__('time').time() * 1000)
#         payload = f"{timestamp}.{self.canonicalize(body)}"
#         digest = hmac.new(
#             key=secret.encode(),
#             msg=payload.encode(),
#             digestmod=hashlib.sha256
#         ).hexdigest()
#         return f"t={timestamp}, v{version}={digest}"
#
#     def add_api_signature_header(self, package_name, instance):
#         body = self.sanitize_body()
#         variables = body['variables'] if body and 'variables' in body else '{}'
#         formatted_body = {**body, 'variables': json.loads(variables)}
#         if package_name == 'backend':
#             signature = self.generate_backend_api_signature(formatted_body)
#         elif package_name == 'auth':
#             signature = self.generate_auth_api_signature(formatted_body)
#         else:
#             signature = self.generate_backend_api_signature(formatted_body)
#         self.req.set_header('signature', signature)
#         if instance == 'sender':
#             self.req.set_header('tenant-id', '438fa74a-fa7d-4317-9ced-dde32ece1787')
#         elif instance == 'receiver':
#             self.req.set_header('tenant-id', '438fa74a-fa7d-4317-9ced-dde32ece1787')
#         else:
#             self.req.set_header('tenant-id', '438fa74a-fa7d-4317-9ced-dde32ece1787')
#
#     def add_host_header(self, host_var_name=None):
#         request_url = urlparse(self.resolve_template_variables(self.req.get_url()))
#         if host_var_name:
#             self.bru.set_env_var(host_var_name, f"{request_url.scheme}//{request_url.netloc}")
#         if request_url.hostname == 'localhost':
#             host_header = (
#                 self.bru.get_env_var('host3000') if request_url.port == 3000
#                 else self.bru.get_env_var('host4000')
#             )
#             self.req.headers['host'] = host_header
#
#     def store_token_details(self):
#         body = self.res.get_body()
#         if body and 'access_token' in body:
#             self.bru.set_env_var('accessToken', body['access_token']['value'])
#             self.bru.set_env_var('tokenId', body['access_token']['manage'].split('/')[-1])
#         if body and 'continue' in body:
#             self.bru.set_env_var('continueToken', body['continue']['access_token']['value'])
#             self.bru.set_env_var('continueId', body['continue']['uri'].split('/')[-1])
#
#     def load_wallet_address_ids_into_variables(self):
#         request_url = self.resolve_template_variables(self.req.url)
#         get_wallet_addresses_query = """
#         query GetWalletAddresses {
#             walletAddresses {
#                 edges {
#                     cursor
#                     node {
#                         id
#                         publicName
#                     }
#                 }
#             }
#         }"""
#         post_body = {"query": get_wallet_addresses_query}
#         post_request = {
#             "method": "post",
#             "headers": {
#                 "signature": self.generate_backend_api_signature(post_body),
#                 "Content-Type": "application/json",
#                 "tenant-id": self.bru.get_env_var('senderTenantId')
#             },
#             "json": post_body
#         }
#         response = requests.post(request_url, **post_request)
#         body = response.json()
#         # Default accounts mapping
#         map_public_name_to_var = {
#             "World's Best Donut Co": 'wbdcWalletAddressId',
#             'Bert Hamchest': 'bhamchestWalletAddressId',
#             'Grace Franklin': 'gfranklinWalletAddressId',
#             'Philip Fry': 'pfryWalletAddressId',
#             'PlanEx Corp': 'planexWalletAddressId',
#             'Lars': 'larsWalletAddressId',
#             'David': 'davidWalletAddressId'
#         }
#         for edge in body['data']['walletAddresses']['edges']:
#             node = edge['node']
#             var_name = map_public_name_to_var.get(node['publicName'])
#             if var_name:
#                 self.bru.set_env_var(var_name, node['id'])

# Aquí termina el módulo Scripts.