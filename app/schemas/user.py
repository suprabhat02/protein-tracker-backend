from datetime import datetime
from pydantic import BaseModel, EmailStr, Field


class UserResponse(BaseModel):
    id: str
    email: EmailStr
    full_name: str
    avatar_url: str | None = None
    daily_protein_target: int
    preferences: dict[str, str | int | bool]
    created_at: datetime
    updated_at: datetime


class UpdateProfileRequest(BaseModel):
    full_name: str = Field(min_length=2, max_length=120)
    daily_protein_target: int = Field(ge=30, le=450)
    preferences: dict[str, str | int | bool] = Field(default_factory=dict)
