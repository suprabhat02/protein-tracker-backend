from datetime import UTC, datetime
from app.repositories.food_log_repository import FoodLogRepository
from app.repositories.user_repository import UserRepository
from app.schemas.dashboard import DashboardResponse, DailyProgress
from app.schemas.food_log import FoodLogResponse


class DashboardService:
    def __init__(
        self, user_repository: UserRepository, food_log_repository: FoodLogRepository
    ) -> None:
        self.user_repository = user_repository
        self.food_log_repository = food_log_repository

    def _food_response(self, log: dict) -> FoodLogResponse:
        return FoodLogResponse(
            id=str(log["_id"]),
            food_name=log["food_name"],
            protein_grams=float(log["protein_grams"]),
            quantity=float(log["quantity"]),
            unit=log["unit"],
            log_date=datetime.fromisoformat(log["log_date"]).date(),
            notes=log.get("notes"),
            created_at=log["created_at"],
            updated_at=log["updated_at"],
        )

    async def get_daily_dashboard(self, user_id: str) -> DashboardResponse:
        user = await self.user_repository.find_by_id(user_id)
        if user is None:
            raise RuntimeError("User not found")

        today = datetime.now(UTC).date()
        logs = await self.food_log_repository.list_by_date(user_id, today)
        consumed = sum(float(log["protein_grams"]) for log in logs)
        target = int(user["daily_protein_target"])

        return DashboardResponse(
            progress=DailyProgress(
                target_protein_grams=target,
                consumed_protein_grams=round(consumed, 2),
                remaining_protein_grams=round(max(target - consumed, 0), 2),
            ),
            logs=[self._food_response(item) for item in logs],
        )
