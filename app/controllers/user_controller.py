from app.schemas.user import CreateUserRequest, UpdateProfileRequest, UserResponse
from app.services.user_service import UserService


class UserController:
    def __init__(self, user_service: UserService) -> None:
        self.user_service = user_service

    async def profile(self, user_id: str) -> UserResponse:
        return await self.user_service.get_profile(user_id)

    async def update_profile(
        self, user_id: str, payload: UpdateProfileRequest
    ) -> UserResponse:
        return await self.user_service.update_profile(user_id, payload)

    async def create_user(self, payload: CreateUserRequest) -> UserResponse:
        return await self.user_service.create_user(payload)

    async def get_profile_by_email(self, email: str) -> UserResponse:
        return await self.user_service.get_profile_by_email(email)

    async def update_profile_by_email(
        self, email: str, payload: UpdateProfileRequest
    ) -> UserResponse:
        return await self.user_service.update_profile_by_email(email, payload)

    async def delete_user_by_email(self, email: str) -> None:
        await self.user_service.delete_user_by_email(email)
