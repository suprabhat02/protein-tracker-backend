from google.auth.transport import requests as google_requests
from google.oauth2 import id_token
from app.core.config import get_settings
from app.core.exceptions import AppException
from app.repositories.session_repository import SessionRepository
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserResponse
from app.services.audit_service import AuditService
from app.services.token_service import TokenService
from app.utils.hashids import encode_identifier


class AuthService:
    def __init__(
        self,
        user_repository: UserRepository,
        session_repository: SessionRepository,
        token_service: TokenService,
        audit_service: AuditService,
    ) -> None:
        self.user_repository = user_repository
        self.session_repository = session_repository
        self.token_service = token_service
        self.audit_service = audit_service

    def _to_user_response(self, user_doc: dict) -> UserResponse:
        from app.schemas.user import LifestyleGoal
        lifestyle_raw = user_doc.get("lifestyle")
        lifestyle = LifestyleGoal(lifestyle_raw) if lifestyle_raw else None
        # Fallback to encoded _id if public_id is missing
        public_id = user_doc.get("public_id") or encode_identifier(str(user_doc["_id"]))
        return UserResponse(
            id=public_id,
            email=user_doc["email"],
            full_name=user_doc["full_name"],
            daily_protein_target=user_doc["daily_protein_target"],
            weight_kg=user_doc.get("weight_kg"),
            height_cm=user_doc.get("height_cm"),
            lifestyle=lifestyle,
            created_at=user_doc["created_at"],
            updated_at=user_doc["updated_at"],
        )

    async def login_with_google(
        self,
        *,
        google_id_token: str,
        ip_address: str | None,
        user_agent: str | None,
    ) -> tuple[UserResponse, str, str, str]:
        settings = get_settings()

        try:
            idinfo = id_token.verify_oauth2_token(
                google_id_token,
                google_requests.Request(),
                settings.google_client_id,
            )
        except Exception as exc:
            await self.audit_service.record(
                user_id=None,
                event="auth.google.failed",
                actor="anonymous",
                ip_address=ip_address,
                user_agent=user_agent,
                metadata={"error": str(exc)},
            )
            raise AppException(
                "GOOGLE_TOKEN_INVALID", "Google token verification failed.", 401
            ) from exc

        provider_sub = str(idinfo.get("sub", ""))
        email = str(idinfo.get("email", "")).lower()
        full_name = str(idinfo.get("name", "")).strip()
        avatar_url = str(idinfo.get("picture")) if idinfo.get("picture") else None

        if not email or not provider_sub:
            raise AppException(
                "GOOGLE_PROFILE_INVALID", "Google identity payload is incomplete.", 401
            )

        user_doc = await self.user_repository.find_by_provider("google", provider_sub)
        if user_doc is None:
            user_doc = await self.user_repository.find_by_email(email)
        if user_doc is None:
            user_doc = await self.user_repository.create_google_user(
                email=email,
                full_name=full_name or email.split("@")[0],
                provider_sub=provider_sub,
            )

        access_token, refresh_token, session_id, _, csrf_token = (
            self.token_service.issue_session_tokens(str(user_doc["_id"]))
        )
        await self.session_repository.create_session(
            session_id=session_id,
            user_id=str(user_doc["_id"]),
            refresh_token_hash=self.token_service.hash_refresh_token(refresh_token),
            ip_address=ip_address,
            user_agent=user_agent,
        )

        await self.audit_service.record(
            user_id=str(user_doc["_id"]),
            event="auth.login.success",
            actor="user",
            ip_address=ip_address,
            user_agent=user_agent,
            metadata={"provider": "google", "session_id": session_id},
        )

        return self._to_user_response(user_doc), access_token, refresh_token, csrf_token

    async def refresh(
        self,
        *,
        refresh_token: str,
        ip_address: str | None,
        user_agent: str | None,
    ) -> tuple[str, str, str]:
        try:
            payload = self.token_service.parse_refresh_token(refresh_token)
        except Exception as exc:
            raise AppException(
                "REFRESH_TOKEN_INVALID", "Refresh token is invalid.", 401
            ) from exc

        if payload.get("type") != "refresh":
            raise AppException(
                "REFRESH_TOKEN_INVALID", "Refresh token type is invalid.", 401
            )

        user_id = str(payload.get("sub"))
        session_id = str(payload.get("sid"))
        session = await self.session_repository.find_active_session(session_id)
        if session is None or session.get("user_id") != user_id:
            raise AppException("SESSION_NOT_FOUND", "Session is not active.", 401)

        if not self.token_service.verify_refresh_token_hash(
            refresh_token, session["refresh_token_hash"]
        ):
            await self.session_repository.invalidate_session(session_id)
            await self.audit_service.record(
                user_id=user_id,
                event="auth.refresh.replay_detected",
                actor="user",
                ip_address=ip_address,
                user_agent=user_agent,
                metadata={"session_id": session_id},
            )
            raise AppException(
                "REFRESH_REPLAY_DETECTED",
                "Session invalidated due to token replay.",
                401,
            )

        access_token, new_refresh_token, _, csrf_token = (
            self.token_service.rotate_tokens(user_id, session_id)
        )
        new_refresh_hash = self.token_service.hash_refresh_token(new_refresh_token)
        await self.session_repository.rotate_refresh_hash(session_id, new_refresh_hash)

        await self.audit_service.record(
            user_id=user_id,
            event="auth.refresh.success",
            actor="user",
            ip_address=ip_address,
            user_agent=user_agent,
            metadata={"session_id": session_id},
        )

        return access_token, new_refresh_token, csrf_token

    async def logout(
        self,
        *,
        access_token: str,
        ip_address: str | None,
        user_agent: str | None,
    ) -> None:
        try:
            payload = self.token_service.parse_access_token(access_token)
        except Exception as exc:
            raise AppException(
                "ACCESS_TOKEN_INVALID", "Access token is invalid.", 401
            ) from exc

        session_id = str(payload.get("sid"))
        user_id = str(payload.get("sub"))

        await self.session_repository.invalidate_session(session_id)
        await self.audit_service.record(
            user_id=user_id,
            event="auth.logout.success",
            actor="user",
            ip_address=ip_address,
            user_agent=user_agent,
            metadata={"session_id": session_id},
        )
