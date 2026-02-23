from pymongo import ASCENDING, DESCENDING
from motor.motor_asyncio import AsyncIOMotorDatabase


async def ensure_indexes(db: AsyncIOMotorDatabase) -> None:
    await db.users.create_index([("email", ASCENDING)], unique=True, name="uniq_email")
    await db.users.create_index(
        [("provider", ASCENDING), ("provider_sub", ASCENDING)],
        unique=True,
        name="uniq_provider_sub",
    )
    await db.users.create_index(
        [("public_id", ASCENDING)], unique=True, name="uniq_user_public_id"
    )

    await db.sessions.create_index(
        [("session_id", ASCENDING)], unique=True, name="uniq_session_id"
    )
    await db.sessions.create_index(
        [("user_id", ASCENDING), ("created_at", DESCENDING)], name="idx_user_sessions"
    )
    await db.sessions.create_index(
        "expires_at", expireAfterSeconds=0, name="ttl_sessions"
    )

    await db.audit_logs.create_index(
        [("user_id", ASCENDING), ("created_at", DESCENDING)], name="idx_user_audit"
    )
    await db.audit_logs.create_index(
        [("event", ASCENDING), ("created_at", DESCENDING)], name="idx_event_audit"
    )

    await db.food_logs.create_index(
        [("user_id", ASCENDING), ("log_date", DESCENDING)], name="idx_user_log_date"
    )
    await db.food_logs.create_index(
        [("user_id", ASCENDING), ("created_at", DESCENDING)],
        name="idx_user_food_created",
    )
