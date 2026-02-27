from fastapi import APIRouter, Depends, HTTPException, Request, Response, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.controllers.auth_controller import AuthController
from app.core.exceptions import AppException
from app.core.rate_limit import limiter
from app.core.responses import ApiResponse
from app.db.mongo import get_database
from app.dependencies.auth import get_access_token
from app.dependencies.container import get_auth_service
from app.schemas.auth import AuthTokensResponse, FetchTokenRequest, FetchTokenResponse, GoogleLoginRequest, RefreshResponse
from app.services.auth_service import AuthService

bearer_scheme = HTTPBearer()

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


@router.get("/check-user", response_model=ApiResponse[dict])
async def check_user(
    credentials: HTTPAuthorizationCredentials = Security(bearer_scheme),
    db: AsyncIOMotorDatabase = Depends(get_database),
    controller: AuthController = Depends(get_auth_controller),
) -> ApiResponse[dict]:
    try:
        user = await controller.check_user_by_token(token=credentials.credentials, db=db)
    except ValueError as exc:
        raise HTTPException(status_code=401, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=401, detail=f"Token verification failed: {str(exc)}")
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return ApiResponse(data=user)


@router.post("/fetch/token", response_model=ApiResponse[FetchTokenResponse])
async def fetch_token(
    payload: FetchTokenRequest,
    db: AsyncIOMotorDatabase = Depends(get_database),
    controller: AuthController = Depends(get_auth_controller),
) -> ApiResponse[FetchTokenResponse]:
    try:
        result = await controller.fetch_token(google_id_token=payload.id_token, db=db)
    except ValueError as exc:
        raise HTTPException(status_code=401, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=401, detail=f"Token verification failed: {str(exc)}")
    return ApiResponse(data=result)
