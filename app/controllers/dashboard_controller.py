from app.schemas.common import PaginationQuery
from app.schemas.dashboard import DashboardResponse
from app.schemas.food_log import (
    FoodLogCreateRequest,
    FoodLogResponse,
    FoodLogUpdateRequest,
)
from app.services.dashboard_service import DashboardService
from app.services.food_log_service import FoodLogService


class DashboardController:
    def __init__(
        self, dashboard_service: DashboardService, food_log_service: FoodLogService
    ) -> None:
        self.dashboard_service = dashboard_service
        self.food_log_service = food_log_service

    async def dashboard(self, user_id: str) -> DashboardResponse:
        return await self.dashboard_service.get_daily_dashboard(user_id)

    async def create_log(
        self, user_id: str, payload: FoodLogCreateRequest
    ) -> FoodLogResponse:
        return await self.food_log_service.create(user_id, payload)

    async def list_logs(
        self, user_id: str, pagination: PaginationQuery
    ) -> tuple[list[FoodLogResponse], int]:
        return await self.food_log_service.list_paginated(
            user_id, pagination.page, pagination.page_size
        )

    async def update_log(
        self, user_id: str, log_id: str, payload: FoodLogUpdateRequest
    ) -> FoodLogResponse:
        return await self.food_log_service.update(user_id, log_id, payload)

    async def delete_log(self, user_id: str, log_id: str) -> None:
        await self.food_log_service.delete(user_id, log_id)
