from datetime import UTC, datetime, timedelta
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.core.config import get_settings


class SessionRepository:
    def __init__(self, db: AsyncIOMotorDatabase) -> None:
        self.collection = db.sessions

    async def create_session(
        self,
        *,
        session_id: str,
        user_id: str,
        refresh_token_hash: str,
        ip_address: str | None,
        user_agent: str | None,
    ) -> dict:
        now = datetime.now(UTC)
        settings = get_settings()
        document = {
            "session_id": session_id,
            "user_id": user_id,
            "refresh_token_hash": refresh_token_hash,
            "ip_address": ip_address,
            "user_agent": user_agent,
            "rotated_at": None,
            "created_at": now,
            "expires_at": now + timedelta(days=settings.jwt_refresh_ttl_days),
            "invalidated_at": None,
        }
        await self.collection.insert_one(document)
        return document

    async def find_active_session(self, session_id: str) -> dict | None:
        return await self.collection.find_one(
            {"session_id": session_id, "invalidated_at": None}
        )

    async def rotate_refresh_hash(
        self, session_id: str, refresh_token_hash: str
    ) -> None:
        now = datetime.now(UTC)
        await self.collection.update_one(
            {"session_id": session_id, "invalidated_at": None},
            {"$set": {"refresh_token_hash": refresh_token_hash, "rotated_at": now}},
        )

    async def invalidate_session(self, session_id: str) -> None:
        now = datetime.now(UTC)
        await self.collection.update_one(
            {"session_id": session_id, "invalidated_at": None},
            {"$set": {"invalidated_at": now}},
        )

    async def invalidate_user_sessions(self, user_id: str) -> int:
        now = datetime.now(UTC)
        result = await self.collection.update_many(
            {"user_id": user_id, "invalidated_at": None},
            {"$set": {"invalidated_at": now}},
        )
        return result.modified_count
