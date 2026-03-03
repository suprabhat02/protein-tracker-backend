from fastapi import APIRouter, Depends
from app.controllers.user_controller import UserController
from app.core.responses import ApiResponse
from app.dependencies.auth import get_current_user_id
from app.dependencies.container import get_user_service
from app.schemas.user import CreateUserRequest, UpdateProfileRequest, UserResponse
from app.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["users"])


def get_user_controller(
    user_service: UserService = Depends(get_user_service),
) -> UserController:
    return UserController(user_service)


@router.post("", response_model=ApiResponse[UserResponse], status_code=201)
async def create_user(
    payload: CreateUserRequest,
    controller: UserController = Depends(get_user_controller),
) -> ApiResponse[UserResponse]:
    result = await controller.create_user(payload)
    return ApiResponse(data=result)


@router.get("/me", response_model=ApiResponse[UserResponse])
async def profile(
    email: str,
    controller: UserController = Depends(get_user_controller),
) -> ApiResponse[UserResponse]:
    result = await controller.get_profile_by_email(email)
    return ApiResponse(data=result)


@router.put("/me", response_model=ApiResponse[UserResponse])
async def update_profile(
    email: str,
    payload: UpdateProfileRequest,
    controller: UserController = Depends(get_user_controller),
) -> ApiResponse[UserResponse]:
    result = await controller.update_profile_by_email(email, payload)
    return ApiResponse(data=result)
