import secrets
import uuid
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_access_token,
    decode_refresh_token,
    hash_value,
    verify_hash,
)


class TokenService:
    def issue_session_tokens(self, user_id: str) -> tuple[str, str, str, str, str]:
        session_id = str(uuid.uuid4())
        refresh_jti = str(uuid.uuid4())
        csrf_token = secrets.token_urlsafe(32)
        access_token = create_access_token(user_id, session_id, csrf_token)
        refresh_token = create_refresh_token(user_id, session_id, refresh_jti)
        return access_token, refresh_token, session_id, refresh_jti, csrf_token

    def rotate_tokens(self, user_id: str, session_id: str) -> tuple[str, str, str, str]:
        refresh_jti = str(uuid.uuid4())
        csrf_token = secrets.token_urlsafe(32)
        access_token = create_access_token(user_id, session_id, csrf_token)
        refresh_token = create_refresh_token(user_id, session_id, refresh_jti)
        return access_token, refresh_token, refresh_jti, csrf_token

    def hash_refresh_token(self, refresh_token: str) -> str:
        return hash_value(refresh_token)

    def verify_refresh_token_hash(self, refresh_token: str, refresh_hash: str) -> bool:
        return verify_hash(refresh_token, refresh_hash)

    def parse_access_token(self, token: str) -> dict:
        return decode_access_token(token)

    def parse_refresh_token(self, token: str) -> dict:
        return decode_refresh_token(token)
