from app.schemas.user import UpdateProfileRequest, UserResponse
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
