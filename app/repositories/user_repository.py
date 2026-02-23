from datetime import UTC, datetime
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.utils.hashids import encode_identifier


class UserRepository:
    def __init__(self, db: AsyncIOMotorDatabase) -> None:
        self.collection = db.users

    async def find_by_id(self, user_id: str) -> dict | None:
        return await self.collection.find_one({"_id": ObjectId(user_id)})

    async def find_by_email(self, email: str) -> dict | None:
        return await self.collection.find_one({"email": email.lower()})

    async def find_by_provider(self, provider: str, provider_sub: str) -> dict | None:
        return await self.collection.find_one(
            {"provider": provider, "provider_sub": provider_sub}
        )

    async def create_google_user(
        self,
        *,
        email: str,
        full_name: str,
        avatar_url: str | None,
        provider_sub: str,
    ) -> dict:
        now = datetime.now(UTC)
        document = {
            "email": email.lower(),
            "full_name": full_name,
            "avatar_url": avatar_url,
            "provider": "google",
            "provider_sub": provider_sub,
            "daily_protein_target": 120,
            "preferences": {"unit_system": "metric", "theme": "system"},
            "created_at": now,
            "updated_at": now,
        }
        result = await self.collection.insert_one(document)
        await self.collection.update_one(
            {"_id": result.inserted_id},
            {"$set": {"public_id": encode_identifier(str(result.inserted_id))}},
        )
        return await self.collection.find_one({"_id": result.inserted_id})

    async def update_profile(
        self,
        user_id: str,
        *,
        full_name: str,
        daily_protein_target: int,
        preferences: dict,
    ) -> dict:
        now = datetime.now(UTC)
        await self.collection.update_one(
            {"_id": ObjectId(user_id)},
            {
                "$set": {
                    "full_name": full_name,
                    "daily_protein_target": daily_protein_target,
                    "preferences": preferences,
                    "updated_at": now,
                }
            },
        )
        user = await self.find_by_id(user_id)
        if user is None:
            raise RuntimeError("User not found after update.")
        return user
