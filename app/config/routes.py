from fastapi import APIRouter
from app.api.v1.endpoints import (
    auth_router,
    dashboard_router,
    health_router,
    user_router,
)


def register_routes() -> APIRouter:
    router = APIRouter()
    router.include_router(health_router.router)
    router.include_router(auth_router.router)
    router.include_router(user_router.router)
    router.include_router(dashboard_router.router)
    return router
