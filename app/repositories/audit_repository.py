from datetime import UTC, datetime
from motor.motor_asyncio import AsyncIOMotorDatabase


class AuditRepository:
    def __init__(self, db: AsyncIOMotorDatabase) -> None:
        self.collection = db.audit_logs

    async def log_event(
        self,
        *,
        user_id: str | None,
        event: str,
        actor: str,
        ip_address: str | None,
        user_agent: str | None,
        metadata: dict,
    ) -> None:
        await self.collection.insert_one(
            {
                "user_id": user_id,
                "event": event,
                "actor": actor,
                "ip_address": ip_address,
                "user_agent": user_agent,
                "metadata": metadata,
                "created_at": datetime.now(UTC),
            }
        )
