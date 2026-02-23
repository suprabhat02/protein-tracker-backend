from datetime import datetime
from app.core.exceptions import AppException
from app.repositories.food_log_repository import FoodLogRepository
from app.schemas.food_log import (
    FoodLogCreateRequest,
    FoodLogResponse,
    FoodLogUpdateRequest,
)


class FoodLogService:
    def __init__(self, food_log_repository: FoodLogRepository) -> None:
        self.food_log_repository = food_log_repository

    def _to_response(self, item: dict) -> FoodLogResponse:
        return FoodLogResponse(
            id=str(item["_id"]),
            food_name=item["food_name"],
            protein_grams=float(item["protein_grams"]),
            quantity=float(item["quantity"]),
            unit=item["unit"],
            log_date=datetime.fromisoformat(item["log_date"]).date(),
            notes=item.get("notes"),
            created_at=item["created_at"],
            updated_at=item["updated_at"],
        )

    async def create(
        self, user_id: str, payload: FoodLogCreateRequest
    ) -> FoodLogResponse:
        item = await self.food_log_repository.create(
            user_id=user_id,
            food_name=payload.food_name.strip(),
            protein_grams=payload.protein_grams,
            quantity=payload.quantity,
            unit=payload.unit.strip(),
            log_date=payload.log_date,
            notes=payload.notes,
        )
        return self._to_response(item)

    async def list_paginated(
        self, user_id: str, page: int, page_size: int
    ) -> tuple[list[FoodLogResponse], int]:
        items, total = await self.food_log_repository.list_paginated(
            user_id, page, page_size
        )
        return [self._to_response(item) for item in items], total

    async def update(
        self, user_id: str, log_id: str, payload: FoodLogUpdateRequest
    ) -> FoodLogResponse:
        updated = await self.food_log_repository.update(
            log_id, user_id, payload.model_dump()
        )
        if updated is None:
            raise AppException("FOOD_LOG_NOT_FOUND", "Food log entry not found.", 404)
        return self._to_response(updated)

    async def delete(self, user_id: str, log_id: str) -> None:
        deleted = await self.food_log_repository.delete(log_id, user_id)
        if deleted == 0:
            raise AppException("FOOD_LOG_NOT_FOUND", "Food log entry not found.", 404)
