from fastapi import APIRouter, Depends, Query
from app.controllers.dashboard_controller import DashboardController
from app.core.responses import ApiResponse, PaginationMeta
from app.dependencies.auth import get_current_user_id
from app.dependencies.container import get_dashboard_service, get_food_log_service
from app.schemas.common import PaginationQuery
from app.schemas.dashboard import DashboardResponse
from app.schemas.food_log import (
    FoodLogCreateRequest,
    FoodLogResponse,
    FoodLogUpdateRequest,
)
from app.services.dashboard_service import DashboardService
from app.services.food_log_service import FoodLogService

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


def get_dashboard_controller(
    dashboard_service: DashboardService = Depends(get_dashboard_service),
    food_log_service: FoodLogService = Depends(get_food_log_service),
) -> DashboardController:
    return DashboardController(dashboard_service, food_log_service)


@router.get("", response_model=ApiResponse[DashboardResponse])
async def get_dashboard(
    user_id: str = Depends(get_current_user_id),
    controller: DashboardController = Depends(get_dashboard_controller),
) -> ApiResponse[DashboardResponse]:
    result = await controller.dashboard(user_id)
    return ApiResponse(data=result)


@router.post("/logs", response_model=ApiResponse[FoodLogResponse])
async def create_log(
    payload: FoodLogCreateRequest,
    user_id: str = Depends(get_current_user_id),
    controller: DashboardController = Depends(get_dashboard_controller),
) -> ApiResponse[FoodLogResponse]:
    result = await controller.create_log(user_id, payload)
    return ApiResponse(data=result)


@router.get("/logs", response_model=ApiResponse[list[FoodLogResponse]])
async def list_logs(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    user_id: str = Depends(get_current_user_id),
    controller: DashboardController = Depends(get_dashboard_controller),
) -> ApiResponse[list[FoodLogResponse]]:
    pagination = PaginationQuery(page=page, page_size=page_size)
    result, total = await controller.list_logs(user_id, pagination)
    return ApiResponse(
        data=result,
        meta=PaginationMeta(
            page=pagination.page, page_size=pagination.page_size, total=total
        ),
    )


@router.put("/logs/{log_id}", response_model=ApiResponse[FoodLogResponse])
async def update_log(
    log_id: str,
    payload: FoodLogUpdateRequest,
    user_id: str = Depends(get_current_user_id),
    controller: DashboardController = Depends(get_dashboard_controller),
) -> ApiResponse[FoodLogResponse]:
    result = await controller.update_log(user_id, log_id, payload)
    return ApiResponse(data=result)


@router.delete("/logs/{log_id}", response_model=ApiResponse[dict[str, str]])
async def delete_log(
    log_id: str,
    user_id: str = Depends(get_current_user_id),
    controller: DashboardController = Depends(get_dashboard_controller),
) -> ApiResponse[dict[str, str]]:
    await controller.delete_log(user_id, log_id)
    return ApiResponse(data={"message": "Food log deleted."})
