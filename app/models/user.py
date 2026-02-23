from datetime import datetime
from pydantic import BaseModel, EmailStr


class UserModel(BaseModel):
    id: str
    public_id: str
    email: EmailStr
    full_name: str
    avatar_url: str | None = None
    provider: str
    provider_sub: str
    daily_protein_target: int
    preferences: dict[str, str | int | bool]
    created_at: datetime
    updated_at: datetime
