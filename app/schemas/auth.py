from pydantic import BaseModel, Field
from app.schemas.user import UserResponse


class GoogleLoginRequest(BaseModel):
    id_token: str = Field(min_length=20)


class AuthTokensResponse(BaseModel):
    csrf_token: str
    user: UserResponse


class RefreshResponse(BaseModel):
    csrf_token: str


class FetchTokenRequest(BaseModel):
    id_token: str = Field(min_length=20, description="Google ID token")


class FetchTokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict
