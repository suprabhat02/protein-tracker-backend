from datetime import UTC, datetime, timedelta
from typing import Any
from jose import jwt
from passlib.context import CryptContext
from app.core.config import get_settings


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def utc_now() -> datetime:
    return datetime.now(UTC)


def hash_value(value: str) -> str:
    return pwd_context.hash(value)


def verify_hash(plain_value: str, hashed_value: str) -> bool:
    return pwd_context.verify(plain_value, hashed_value)


def create_access_token(subject: str, session_id: str, csrf_token: str) -> str:
    settings = get_settings()
    now = utc_now()
    payload: dict[str, Any] = {
        "sub": subject,
        "sid": session_id,
        "csrf": csrf_token,
        "type": "access",
        "iat": int(now.timestamp()),
        "exp": int(
            (now + timedelta(minutes=settings.jwt_access_ttl_minutes)).timestamp()
        ),
    }
    return jwt.encode(payload, settings.jwt_access_secret, algorithm="HS256")


def create_refresh_token(subject: str, session_id: str, token_id: str) -> str:
    settings = get_settings()
    now = utc_now()
    payload: dict[str, Any] = {
        "sub": subject,
        "sid": session_id,
        "jti": token_id,
        "type": "refresh",
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(days=settings.jwt_refresh_ttl_days)).timestamp()),
    }
    return jwt.encode(payload, settings.jwt_refresh_secret, algorithm="HS256")


def decode_access_token(token: str) -> dict[str, Any]:
    settings = get_settings()
    return jwt.decode(token, settings.jwt_access_secret, algorithms=["HS256"])


def decode_refresh_token(token: str) -> dict[str, Any]:
    settings = get_settings()
    return jwt.decode(token, settings.jwt_refresh_secret, algorithms=["HS256"])
