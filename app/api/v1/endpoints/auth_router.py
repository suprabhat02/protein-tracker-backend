from fastapi import APIRouter, Depends, Request, Response
from app.controllers.auth_controller import AuthController
from app.core.exceptions import AppException
from app.core.rate_limit import limiter
from app.core.responses import ApiResponse
from app.dependencies.auth import get_access_token
from app.dependencies.container import get_auth_service
from app.schemas.auth import AuthTokensResponse, GoogleLoginRequest, RefreshResponse
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


def get_auth_controller(
    auth_service: AuthService = Depends(get_auth_service),
) -> AuthController:
    return AuthController(auth_service)


@router.post("/google/login", response_model=ApiResponse[AuthTokensResponse])
@limiter.limit("20/minute")
async def google_login(
    payload: GoogleLoginRequest,
    request: Request,
    response: Response,
    controller: AuthController = Depends(get_auth_controller),
) -> ApiResponse[AuthTokensResponse]:
    result = await controller.google_login(request, response, payload)
    return ApiResponse(data=result)


@router.post("/refresh", response_model=ApiResponse[RefreshResponse])
@limiter.limit("40/minute")
async def refresh(
    request: Request,
    response: Response,
    controller: AuthController = Depends(get_auth_controller),
) -> ApiResponse[RefreshResponse]:
    try:
        result = await controller.refresh(request, response)
    except ValueError as exc:
        raise AppException("REFRESH_TOKEN_MISSING", str(exc), 401) from exc
    return ApiResponse(data=result)


@router.post("/logout", response_model=ApiResponse[dict[str, str]])
@limiter.limit("40/minute")
async def logout(
    request: Request,
    response: Response,
    access_token: str = Depends(get_access_token),
    controller: AuthController = Depends(get_auth_controller),
) -> ApiResponse[dict[str, str]]:
    await controller.logout(request, response, access_token)
    return ApiResponse(data={"message": "Logged out successfully."})
