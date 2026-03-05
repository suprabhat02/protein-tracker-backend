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
        provider_sub: str,
        weight_kg: float | None = None,
        height_cm: float | None = None,
        lifestyle: str | None = None,
        daily_protein_target: int = 120,
    ) -> dict:
        now = datetime.now(UTC)
        document = {
            "email": email.lower(),
            "full_name": full_name,
            "provider": "google",
            "provider_sub": provider_sub,
            "daily_protein_target": daily_protein_target,
            "weight_kg": weight_kg,
            "height_cm": height_cm,
            "lifestyle": lifestyle,
            "created_at": now,
            "updated_at": now,
        }
        result = await self.collection.insert_one(document)
        await self.collection.update_one(
            {"_id": result.inserted_id},
            {"$set": {"public_id": encode_identifier(str(result.inserted_id))}},
        )
        return await self.collection.find_one({"_id": result.inserted_id})

    async def create_user(
        self,
        *,
        email: str,
        full_name: str,
        weight_kg: float,
        height_cm: float,
        lifestyle: str,
        daily_protein_target: int,
    ) -> dict:
        now = datetime.now(UTC)
        document = {
            "email": email.lower(),
            "full_name": full_name,
            "daily_protein_target": daily_protein_target,
            "weight_kg": weight_kg,
            "height_cm": height_cm,
            "lifestyle": lifestyle,
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
        weight_kg: float | None = None,
        height_cm: float | None = None,
        lifestyle: str | None = None,
    ) -> dict:
        now = datetime.now(UTC)
        update_fields: dict = {
            "full_name": full_name,
            "daily_protein_target": daily_protein_target,
            "updated_at": now,
        }
        if weight_kg is not None:
            update_fields["weight_kg"] = weight_kg
        if height_cm is not None:
            update_fields["height_cm"] = height_cm
        if lifestyle is not None:
            update_fields["lifestyle"] = lifestyle
        await self.collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": update_fields},
        )
        user = await self.find_by_id(user_id)
        if user is None:
            raise RuntimeError("User not found after update.")
        return user

    async def delete_user(self, user_id: str) -> None:
        result = await self.collection.delete_one({"_id": ObjectId(user_id)})
        if result.deleted_count == 0:
            raise RuntimeError("User not found or already deleted.")
