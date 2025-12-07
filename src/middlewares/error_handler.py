from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

import traceback
import logging

logger = logging.getLogger("error_handler")


async def error_middleware(request: Request, call_next):
    try:
        response = await call_next(request)
        return response

    except HTTPException as e:
        # Respeta el status code y el detail
        logger.warning(f"HTTPException: {e.detail}")
        return JSONResponse(
            status_code=e.status_code,
            content={"error": e.detail}
        )

    except RequestValidationError as e:
        # Errores de validación 422 automáticos de FastAPI
        logger.warning(f"Validation error: {e.errors()}")
        return JSONResponse(
            status_code=422,
            content={
                "error": "Validation error",
                "details": e.errors()
            }
        )

    except IntegrityError as e:
        # Errores por duplicados o constraints
        logger.error(f"IntegrityError: {str(e.orig)}")
        return JSONResponse(
            status_code=409,
            content={
                "error": "Database integrity error",
                "details": str(e.orig)
            }
        )

    except SQLAlchemyError as e:
        # Cualquier otro error SQL
        logger.error(f"SQLAlchemyError: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={
                "error": "Database error",
                "details": str(e)
            }
        )

    except Exception as e:
        # Cualquier error inesperado
        logger.error(f"Unhandled error: {e}")
        logger.error(traceback.format_exc())  # Log full stacktrace

        return JSONResponse(
            status_code=500,
            content={
                "error": "Internal server error",
                "details": str(e)
            }
        )
