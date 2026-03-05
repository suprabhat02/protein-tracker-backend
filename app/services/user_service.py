from bson import ObjectId
from app.core.exceptions import AppException
from app.repositories.user_repository import UserRepository
from app.schemas.user import (
    CreateUserRequest,
    LifestyleGoal,
    UpdateProfileRequest,
    UserResponse,
    calculate_protein_target,
)
from app.utils.hashids import encode_identifier


class UserService:
    def __init__(self, user_repository: UserRepository) -> None:
        self.user_repository = user_repository

    def _to_response(self, user_doc: dict) -> UserResponse:
        lifestyle_raw = user_doc.get("lifestyle")
        lifestyle = LifestyleGoal(lifestyle_raw) if lifestyle_raw else None
        # Fallback to encoded _id if public_id is missing
        public_id = user_doc.get("public_id") or encode_identifier(str(user_doc["_id"]))
        return UserResponse(
            id=public_id,
            email=user_doc["email"],
            full_name=user_doc["full_name"],
            daily_protein_target=user_doc["daily_protein_target"],
            weight_kg=user_doc.get("weight_kg"),
            height_cm=user_doc.get("height_cm"),
            lifestyle=lifestyle,
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

        # Auto-recalculate protein target if weight and lifestyle are both provided
        protein_target = payload.daily_protein_target
        if payload.weight_kg and payload.lifestyle:
            protein_target = calculate_protein_target(payload.weight_kg, payload.lifestyle)

        updated = await self.user_repository.update_profile(
            user_id,
            full_name=payload.full_name.strip(),
            daily_protein_target=protein_target,
            weight_kg=payload.weight_kg,
            height_cm=payload.height_cm,
            lifestyle=payload.lifestyle.value if payload.lifestyle else None,
        )
        return self._to_response(updated)

    async def create_user(self, payload: CreateUserRequest) -> UserResponse:
        existing = await self.user_repository.find_by_email(payload.email)
        if existing is not None:
            raise AppException(
                "USER_ALREADY_EXISTS",
                "A user with this email already exists.",
                409,
            )

        daily_protein_target = calculate_protein_target(payload.weight_kg, payload.lifestyle)

        user_doc = await self.user_repository.create_user(
            email=payload.email,
            full_name=payload.full_name.strip(),
            weight_kg=payload.weight_kg,
            height_cm=payload.height_cm,
            lifestyle=payload.lifestyle.value,
            daily_protein_target=daily_protein_target,
        )
        return self._to_response(user_doc)

    async def get_profile_by_email(self, email: str) -> UserResponse:
        user_doc = await self.user_repository.find_by_email(email)
        if user_doc is None:
            raise AppException("USER_NOT_FOUND", "User profile not found.", 404)
        return self._to_response(user_doc)

    async def update_profile_by_email(
        self, email: str, payload: UpdateProfileRequest
    ) -> UserResponse:
        user_doc = await self.user_repository.find_by_email(email)
        if user_doc is None:
            raise AppException("USER_NOT_FOUND", "User not found.", 404)

        user_id = str(user_doc["_id"])

        # Auto-recalculate protein target if weight and lifestyle are both provided
        protein_target = payload.daily_protein_target
        if payload.weight_kg and payload.lifestyle:
            protein_target = calculate_protein_target(payload.weight_kg, payload.lifestyle)

        updated = await self.user_repository.update_profile(
            user_id,
            full_name=payload.full_name.strip(),
            daily_protein_target=protein_target,
            weight_kg=payload.weight_kg,
            height_cm=payload.height_cm,
            lifestyle=payload.lifestyle.value if payload.lifestyle else None,
        )
        return self._to_response(updated)

    async def delete_user_by_email(self, email: str) -> None:
        user_doc = await self.user_repository.find_by_email(email)
        if user_doc is None:
            raise AppException("USER_NOT_FOUND", "User not found.", 404)

        user_id = str(user_doc["_id"])
        await self.user_repository.delete_user(user_id)
