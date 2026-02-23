from fastapi import Request
from fastapi.responses import ORJSONResponse


class AppException(Exception):
    def __init__(self, code: str, message: str, status_code: int = 400) -> None:
        self.code = code
        self.message = message
        self.status_code = status_code
        super().__init__(message)


async def app_exception_handler(_: Request, exc: AppException) -> ORJSONResponse:
    return ORJSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": {
                "code": exc.code,
                "message": exc.message,
                "details": None,
            },
        },
    )


async def generic_exception_handler(_: Request, exc: Exception) -> ORJSONResponse:
    return ORJSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected error occurred.",
                "details": {"reason": str(exc)},
            },
        },
    )
