from fastapi import Depends, Header, Request
from app.core.config import get_settings
from app.core.exceptions import AppException
from app.services.token_service import TokenService


def _extract_bearer_token(authorization: str | None) -> str | None:
    if not authorization:
        return None
    parts = authorization.split(" ", maxsplit=1)
    if len(parts) != 2 or parts[0].lower() != "bearer":
        return None
    return parts[1]


def get_access_token(
    request: Request,
    authorization: str | None = Header(default=None),
) -> str:
    settings = get_settings()
    bearer_token = _extract_bearer_token(authorization)
    cookie_token = request.cookies.get(settings.access_cookie_name)
    token = bearer_token or cookie_token
    if not token:
        raise AppException("AUTH_REQUIRED", "Authentication is required.", 401)
    return token


def get_current_user_id(token: str = Depends(get_access_token)) -> str:
    token_service = TokenService()
    try:
        payload = token_service.parse_access_token(token)
    except Exception as exc:
        raise AppException(
            "ACCESS_TOKEN_INVALID", "Access token is invalid.", 401
        ) from exc

    if payload.get("type") != "access":
        raise AppException("ACCESS_TOKEN_INVALID", "Access token type is invalid.", 401)

    user_id = payload.get("sub")
    if not isinstance(user_id, str) or not user_id:
        raise AppException(
            "ACCESS_TOKEN_INVALID", "Access token subject is invalid.", 401
        )
    return user_id
