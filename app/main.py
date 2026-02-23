from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from app.config.routes import register_routes
from app.core.config import get_settings
from app.core.exceptions import (
    AppException,
    app_exception_handler,
    generic_exception_handler,
)
from app.core.logging import configure_logging
from app.core.middleware import (
    CsrfMiddleware,
    PayloadLimitMiddleware,
    RequestContextMiddleware,
    SecurityHeadersMiddleware,
)
from app.core.rate_limit import limiter
from app.db.indexes import ensure_indexes
from app.db.mongo import mongo_manager


@asynccontextmanager
async def lifespan(_: FastAPI):
    await mongo_manager.connect()
    await ensure_indexes(mongo_manager.db)
    yield
    await mongo_manager.disconnect()


def create_app() -> FastAPI:
    settings = get_settings()
    configure_logging()

    app = FastAPI(title=settings.app_name, lifespan=lifespan)
    app.state.limiter = limiter

    app.add_middleware(SlowAPIMiddleware)
    app.add_middleware(RequestContextMiddleware)
    app.add_middleware(PayloadLimitMiddleware)
    app.add_middleware(CsrfMiddleware)
    app.add_middleware(SecurityHeadersMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_allow_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["Content-Type", "Authorization", "X-CSRF-Token", "X-Request-ID"],
        expose_headers=["X-Request-ID"],
    )

    @app.exception_handler(AppException)
    async def handle_app_exception(request: Request, exc: AppException):
        return await app_exception_handler(request, exc)

    @app.exception_handler(RequestValidationError)
    async def handle_validation_error(_: Request, exc: RequestValidationError):
        return ORJSONResponse(
            status_code=422,
            content={
                "success": False,
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": "Request validation failed.",
                    "details": exc.errors(),
                },
            },
        )

    @app.exception_handler(RateLimitExceeded)
    async def handle_rate_limit(_: Request, __: RateLimitExceeded):
        return ORJSONResponse(
            status_code=429,
            content={
                "success": False,
                "error": {
                    "code": "RATE_LIMIT_EXCEEDED",
                    "message": "Too many requests.",
                    "details": None,
                },
            },
        )

    @app.exception_handler(Exception)
    async def handle_generic_exception(request: Request, exc: Exception):
        return await generic_exception_handler(request, exc)

    api_router = register_routes()
    app.include_router(api_router, prefix=settings.api_prefix)
    return app


app = create_app()
