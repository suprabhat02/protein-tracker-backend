from datetime import datetime
from pydantic import BaseModel


class AuditLogModel(BaseModel):
    user_id: str | None = None
    event: str
    actor: str
    ip_address: str | None = None
    user_agent: str | None = None
    metadata: dict[str, str | int | float | bool | None]
    created_at: datetime
