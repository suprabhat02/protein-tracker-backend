import uuid
from fastapi import Request
from fastapi.responses import ORJSONResponse, Response
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.config import get_settings


class RequestContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = request.headers.get("x-request-id", str(uuid.uuid4()))
        request.state.request_id = request_id
        response: Response = await call_next(request)
        response.headers["x-request-id"] = request_id
        return response


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response: Response = await call_next(request)
        request_path = request.url.path
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = (
            "geolocation=(), camera=(), microphone=()"
        )
        response.headers["Strict-Transport-Security"] = (
            "max-age=31536000; includeSubDomains"
        )
        if request_path in {"/docs", "/redoc", "/openapi.json"}:
            response.headers["Content-Security-Policy"] = (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://unpkg.com; "
                "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://unpkg.com; "
                "img-src 'self' data: https:; "
                "font-src 'self' data: https:"
            )
        else:
            response.headers["Content-Security-Policy"] = "default-src 'self'"
        return response


class PayloadLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        settings = get_settings()
        content_length = request.headers.get("content-length")
        if content_length and int(content_length) > settings.max_payload_bytes:
            return ORJSONResponse(
                status_code=413,
                content={
                    "success": False,
                    "error": {
                        "code": "PAYLOAD_TOO_LARGE",
                        "message": "Request payload exceeds configured limit.",
                        "details": None,
                    },
                },
            )
        return await call_next(request)


class CsrfMiddleware(BaseHTTPMiddleware):
    EXEMPT_PATHS = {
        "/health",
        "/api/v1/auth/google/login",
        "/api/v1/auth/refresh",
        "/api/v1/auth/fetch/token",
        "/api/v1/users",
        "/api/v1/users/me",
    }

    async def dispatch(self, request: Request, call_next):
        settings = get_settings()
        method = request.method.upper()
        if (
            method in {"POST", "PUT", "PATCH", "DELETE"}
            and request.url.path not in self.EXEMPT_PATHS
        ):
            csrf_cookie = request.cookies.get(settings.csrf_cookie_name)
            csrf_header = request.headers.get("x-csrf-token")
            if not csrf_cookie or not csrf_header or csrf_cookie != csrf_header:
                return ORJSONResponse(
                    status_code=403,
                    content={
                        "success": False,
                        "error": {
                            "code": "CSRF_VALIDATION_FAILED",
                            "message": "CSRF validation failed.",
                            "details": None,
                        },
                    },
                )
        return await call_next(request)
