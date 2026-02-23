from pydantic import BaseModel, Field
from app.schemas.user import UserResponse


class GoogleLoginRequest(BaseModel):
    id_token: str = Field(min_length=20)


class AuthTokensResponse(BaseModel):
    csrf_token: str
    user: UserResponse


class RefreshResponse(BaseModel):
    csrf_token: str
