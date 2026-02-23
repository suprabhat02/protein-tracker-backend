from datetime import datetime
from pydantic import BaseModel


class SessionModel(BaseModel):
    session_id: str
    user_id: str
    refresh_token_hash: str
    user_agent: str | None = None
    ip_address: str | None = None
    rotated_at: datetime | None = None
    created_at: datetime
    expires_at: datetime
    invalidated_at: datetime | None = None
