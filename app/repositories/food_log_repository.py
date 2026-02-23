from datetime import UTC, date, datetime
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase


class FoodLogRepository:
    def __init__(self, db: AsyncIOMotorDatabase) -> None:
        self.collection = db.food_logs

    async def create(
        self,
        *,
        user_id: str,
        food_name: str,
        protein_grams: float,
        quantity: float,
        unit: str,
        log_date: date,
        notes: str | None,
    ) -> dict:
        now = datetime.now(UTC)
        document = {
            "user_id": user_id,
            "food_name": food_name,
            "protein_grams": protein_grams,
            "quantity": quantity,
            "unit": unit,
            "log_date": log_date.isoformat(),
            "notes": notes,
            "created_at": now,
            "updated_at": now,
        }
        result = await self.collection.insert_one(document)
        saved = await self.collection.find_one({"_id": result.inserted_id})
        if saved is None:
            raise RuntimeError("Food log create failed")
        return saved

    async def list_by_date(self, user_id: str, log_date: date) -> list[dict]:
        cursor = self.collection.find(
            {"user_id": user_id, "log_date": log_date.isoformat()}
        ).sort("created_at", -1)
        return await cursor.to_list(length=200)

    async def list_paginated(
        self, user_id: str, page: int, page_size: int
    ) -> tuple[list[dict], int]:
        total = await self.collection.count_documents({"user_id": user_id})
        skip = (page - 1) * page_size
        cursor = (
            self.collection.find({"user_id": user_id})
            .sort("log_date", -1)
            .sort("created_at", -1)
            .skip(skip)
            .limit(page_size)
        )
        return await cursor.to_list(length=page_size), total

    async def update(self, log_id: str, user_id: str, payload: dict) -> dict | None:
        payload["updated_at"] = datetime.now(UTC)
        if "log_date" in payload and isinstance(payload["log_date"], date):
            payload["log_date"] = payload["log_date"].isoformat()
        await self.collection.update_one(
            {"_id": ObjectId(log_id), "user_id": user_id},
            {"$set": payload},
        )
        return await self.collection.find_one(
            {"_id": ObjectId(log_id), "user_id": user_id}
        )

    async def delete(self, log_id: str, user_id: str) -> int:
        result = await self.collection.delete_one(
            {"_id": ObjectId(log_id), "user_id": user_id}
        )
        return result.deleted_count
