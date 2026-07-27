# from fastapi import FastAPI, Request
# from fastapi.responses import JSONResponse
# from fastapi.exceptions import RequestValidationError


# def register_exception_handlers(app: FastAPI):

#     @app.exception_handler(RequestValidationError)
#     async def validation_exception_handler(
#         request: Request,
#         exc: RequestValidationError,
#     ):
#         return JSONResponse(
#             status_code=422,
#             content={
#                 "success": False,
#                 "message": "Validation Error",
#                 "errors": exc.errors(),
#             },
#         )

#     @app.exception_handler(Exception)
#     async def global_exception_handler(
#         request: Request,
#         exc: Exception,
#     ):
#         return JSONResponse(
#             status_code=500,
#             content={
#                 "success": False,
#                 "message": str(exc),
#             },
#         )


# api/exception.py
import logging
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

logger = logging.getLogger(__name__)


def register_exception_handlers(app: FastAPI):
    
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request,
        exc: RequestValidationError,
    ):
        logger.warning(f"Validation error: {exc.errors()}")
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "success": False,
                "message": "Validation Error",
                "errors": exc.errors(),
            },
        )

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(
        request: Request,
        exc: StarletteHTTPException,
    ):
        logger.warning(f"HTTP error: {exc.status_code} - {exc.detail}")
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "message": exc.detail,
            },
        )

    @app.exception_handler(Exception)
    async def global_exception_handler(
        request: Request,
        exc: Exception,
    ):
        logger.error(f"Unhandled exception: {exc}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "success": False,
                "message": "Internal server error",
                "detail": str(exc) if app.debug else None,
            },
        )        