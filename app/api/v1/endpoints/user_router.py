from fastapi import APIRouter, Depends
from app.controllers.user_controller import UserController
from app.core.responses import ApiResponse
from app.dependencies.auth import get_current_user_id
from app.dependencies.container import get_user_service
from app.schemas.user import UpdateProfileRequest, UserResponse
from app.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["users"])


def get_user_controller(
    user_service: UserService = Depends(get_user_service),
) -> UserController:
    return UserController(user_service)


@router.get("/me", response_model=ApiResponse[UserResponse])
async def profile(
    user_id: str = Depends(get_current_user_id),
    controller: UserController = Depends(get_user_controller),
) -> ApiResponse[UserResponse]:
    result = await controller.profile(user_id)
    return ApiResponse(data=result)


@router.put("/me", response_model=ApiResponse[UserResponse])
async def update_profile(
    payload: UpdateProfileRequest,
    user_id: str = Depends(get_current_user_id),
    controller: UserController = Depends(get_user_controller),
) -> ApiResponse[UserResponse]:
    result = await controller.update_profile(user_id, payload)
    return ApiResponse(data=result)
