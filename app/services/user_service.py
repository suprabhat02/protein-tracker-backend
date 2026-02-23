from bson import ObjectId
from app.core.exceptions import AppException
from app.repositories.user_repository import UserRepository
from app.schemas.user import UpdateProfileRequest, UserResponse


class UserService:
    def __init__(self, user_repository: UserRepository) -> None:
        self.user_repository = user_repository

    def _to_response(self, user_doc: dict) -> UserResponse:
        return UserResponse(
            id=user_doc["public_id"],
            email=user_doc["email"],
            full_name=user_doc["full_name"],
            avatar_url=user_doc.get("avatar_url"),
            daily_protein_target=user_doc["daily_protein_target"],
            preferences=user_doc.get("preferences", {}),
            created_at=user_doc["created_at"],
            updated_at=user_doc["updated_at"],
        )

    async def get_profile(self, user_id: str) -> UserResponse:
        user_doc = await self.user_repository.find_by_id(user_id)
        if user_doc is None:
            raise AppException("USER_NOT_FOUND", "User profile not found.", 404)
        return self._to_response(user_doc)

    async def update_profile(
        self, user_id: str, payload: UpdateProfileRequest
    ) -> UserResponse:
        if not ObjectId.is_valid(user_id):
            raise AppException("INVALID_USER", "User identifier is invalid.", 400)

        updated = await self.user_repository.update_profile(
            user_id,
            full_name=payload.full_name.strip(),
            daily_protein_target=payload.daily_protein_target,
            preferences=payload.preferences,
        )
        return self._to_response(updated)
