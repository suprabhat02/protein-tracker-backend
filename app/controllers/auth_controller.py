from fastapi import Request, Response
from google.oauth2 import id_token
from google.auth.transport import requests as google_auth_requests
import requests as http_requests
from app.core.config import get_settings
from app.schemas.auth import AuthTokensResponse, GoogleLoginRequest, RefreshResponse
from app.services.auth_service import AuthService
from app.db.mongo import get_database
from motor.motor_asyncio import AsyncIOMotorDatabase


def _set_auth_cookies(
    response: Response, access_token: str, refresh_token: str, csrf_token: str
) -> None:
    settings = get_settings()
    cookie_domain = (
        None if settings.cookie_domain == "localhost" else settings.cookie_domain
    )
    response.set_cookie(
        key=settings.access_cookie_name,
        value=access_token,
        httponly=True,
        secure=settings.cookie_secure,
        samesite="strict",
        domain=cookie_domain,
        max_age=settings.jwt_access_ttl_minutes * 60,
        path="/",
    )
    response.set_cookie(
        key=settings.refresh_cookie_name,
        value=refresh_token,
        httponly=True,
        secure=settings.cookie_secure,
        samesite="strict",
        domain=cookie_domain,
        max_age=settings.jwt_refresh_ttl_days * 24 * 60 * 60,
        path="/api/v1/auth",
    )
    response.set_cookie(
        key=settings.csrf_cookie_name,
        value=csrf_token,
        httponly=False,
        secure=settings.cookie_secure,
        samesite="strict",
        domain=cookie_domain,
        max_age=settings.jwt_refresh_ttl_days * 24 * 60 * 60,
        path="/",
    )


def _clear_auth_cookies(response: Response) -> None:
    settings = get_settings()
    cookie_domain = (
        None if settings.cookie_domain == "localhost" else settings.cookie_domain
    )
    response.delete_cookie(settings.access_cookie_name, domain=cookie_domain, path="/")
    response.delete_cookie(
        settings.refresh_cookie_name, domain=cookie_domain, path="/api/v1/auth"
    )
    response.delete_cookie(settings.csrf_cookie_name, domain=cookie_domain, path="/")


class AuthController:
    def __init__(self, auth_service: AuthService) -> None:
        self.auth_service = auth_service

    async def google_login(
        self, request: Request, response: Response, payload: GoogleLoginRequest
    ) -> AuthTokensResponse:
        ip_address = request.client.host if request.client else None
        user_agent = request.headers.get("user-agent")
        user, access_token, refresh_token, csrf_token = (
            await self.auth_service.login_with_google(
                google_id_token=payload.id_token,
                ip_address=ip_address,
                user_agent=user_agent,
            )
        )
        _set_auth_cookies(response, access_token, refresh_token, csrf_token)
        return AuthTokensResponse(csrf_token=csrf_token, user=user)

    async def refresh(self, request: Request, response: Response) -> RefreshResponse:
        settings = get_settings()
        refresh_token = request.cookies.get(settings.refresh_cookie_name)
        if not refresh_token:
            _clear_auth_cookies(response)
            raise ValueError("Missing refresh token cookie")

        ip_address = request.client.host if request.client else None
        user_agent = request.headers.get("user-agent")
        access_token, new_refresh, csrf_token = await self.auth_service.refresh(
            refresh_token=refresh_token,
            ip_address=ip_address,
            user_agent=user_agent,
        )
        _set_auth_cookies(response, access_token, new_refresh, csrf_token)
        return RefreshResponse(csrf_token=csrf_token)

    async def logout(
        self, request: Request, response: Response, access_token: str
    ) -> None:
        ip_address = request.client.host if request.client else None
        user_agent = request.headers.get("user-agent")
        await self.auth_service.logout(
            access_token=access_token,
            ip_address=ip_address,
            user_agent=user_agent,
        )
        _clear_auth_cookies(response)

    def verify_google_token(self, token: str) -> tuple[str | None, bool]:
        settings = get_settings()
        session = http_requests.Session()
        session.verify = False
        google_request = google_auth_requests.Request(session=session)
        idinfo = id_token.verify_oauth2_token(
            token,
            google_request,
            settings.google_client_id,
        )
        email = idinfo.get("email")
        email_verified = idinfo.get("email_verified", False)
        return email, email_verified

    async def check_user_by_token(self, token: str, db: AsyncIOMotorDatabase) -> dict:
        email, email_verified = self.verify_google_token(token)
        if not email or not email_verified:
            raise ValueError("Google token has unverified or missing email")
        user = await db["users"].find_one({"email": email})
        if not user:
            return None
        return {"id": str(user["_id"]), "fullName": user.get("fullName", ""), "email": user["email"]}

    async def fetch_token(self, google_id_token: str, db: AsyncIOMotorDatabase) -> dict:
        from app.core.security import create_access_token
        import secrets
        import uuid
        email, email_verified = self.verify_google_token(google_id_token)
        if not email or not email_verified:
            raise ValueError("Google token has unverified or missing email")
        user = await db["users"].find_one({"email": email})
        if not user:
            raise ValueError("User not found")
        user_id = str(user["_id"])
        session_id = str(uuid.uuid4())
        csrf_token = secrets.token_urlsafe(32)
        access_token = create_access_token(user_id, session_id, csrf_token)
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": {"id": user_id, "fullName": user.get("fullName", ""), "email": user["email"]},
        }

    async def check_user(self, email: str, db: AsyncIOMotorDatabase) -> dict:
        user = await db["users"].find_one({"email": email})
        if not user:
            return None
        return {"id": str(user["_id"]), "fullName": user.get("fullName", ""), "email": user["email"]}

    async def check_user(self, email: str, db: AsyncIOMotorDatabase) -> dict:
        user = await db["users"].find_one({"email": email})
        if not user:
            return None
        return {"id": str(user["_id"]), "fullName": user["fullName"], "email": user["email"]}
