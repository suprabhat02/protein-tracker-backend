from fastapi import Depends
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.db.mongo import get_database
from app.repositories.audit_repository import AuditRepository
from app.repositories.food_log_repository import FoodLogRepository
from app.repositories.session_repository import SessionRepository
from app.repositories.user_repository import UserRepository
from app.services.audit_service import AuditService
from app.services.auth_service import AuthService
from app.services.dashboard_service import DashboardService
from app.services.food_log_service import FoodLogService
from app.services.token_service import TokenService
from app.services.user_service import UserService


def get_user_repository(
    db: AsyncIOMotorDatabase = Depends(get_database),
) -> UserRepository:
    return UserRepository(db)


def get_session_repository(
    db: AsyncIOMotorDatabase = Depends(get_database),
) -> SessionRepository:
    return SessionRepository(db)


def get_audit_repository(
    db: AsyncIOMotorDatabase = Depends(get_database),
) -> AuditRepository:
    return AuditRepository(db)


def get_food_log_repository(
    db: AsyncIOMotorDatabase = Depends(get_database),
) -> FoodLogRepository:
    return FoodLogRepository(db)


def get_audit_service(
    audit_repository: AuditRepository = Depends(get_audit_repository),
) -> AuditService:
    return AuditService(audit_repository)


def get_token_service() -> TokenService:
    return TokenService()


def get_auth_service(
    user_repository: UserRepository = Depends(get_user_repository),
    session_repository: SessionRepository = Depends(get_session_repository),
    token_service: TokenService = Depends(get_token_service),
    audit_service: AuditService = Depends(get_audit_service),
) -> AuthService:
    return AuthService(
        user_repository, session_repository, token_service, audit_service
    )


def get_user_service(
    user_repository: UserRepository = Depends(get_user_repository),
) -> UserService:
    return UserService(user_repository)


def get_dashboard_service(
    user_repository: UserRepository = Depends(get_user_repository),
    food_log_repository: FoodLogRepository = Depends(get_food_log_repository),
) -> DashboardService:
    return DashboardService(user_repository, food_log_repository)


def get_food_log_service(
    food_log_repository: FoodLogRepository = Depends(get_food_log_repository),
) -> FoodLogService:
    return FoodLogService(food_log_repository)
