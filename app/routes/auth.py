"""
Authentication Routes

Provides endpoints for user registration, login, and token refresh.
"""

from fastapi import APIRouter, Response, status, Depends

from core.dependencies import get_auth_service, get_current_user_id
from core.config import settings
from schema.auth import UserLogin, TokenResponse
from services.auth import AuthService

router = APIRouter(
    prefix="/auth",
    tags=["authentication"],
    responses={
        400: {"description": "Bad request"},
        401: {"description": "Unauthorized"},
        409: {"description": "Conflict (email already exists)"}
    }
)


@router.post(
    "/login",
    status_code=status.HTTP_200_OK,
    response_model=TokenResponse,
    summary="User login",
    description="Authenticate user and receive JWT token"
)
async def login(
    response: Response,
    credentials: UserLogin,
    auth_service: AuthService = Depends(get_auth_service),
) -> TokenResponse:
    """
    Authenticate user and generate JWT access token and refresh token.

    Args:
        credentials: Login credentials (email, password)
        db: Database session

    Returns:
        TokenResponse: JWT access token
    """
    user = await auth_service.authenticate(credentials)
    access_token = await auth_service.refresh_token(response, user.id)
    return TokenResponse(access_token=access_token)


@router.post(
    "/refresh",
    status_code=status.HTTP_200_OK,
    response_model=TokenResponse,
    summary="Refresh access token",
    description="Refresh JWT access token using refresh token")
async def refresh_token(
    response: Response,
    refresh_token: str,
    auth_service: AuthService = Depends(get_auth_service)
) -> TokenResponse:
    """
    Refresh JWT access token using refresh token.

    Args:
        response: FastAPI Response object
        refresh_token (str): current, valid refresh token

    Returns:
        TokenResponse: New JWT access token
    """
    user_id = await auth_service.validate_refresh_token(refresh_token)

    access_token = await auth_service.refresh_token(response, user_id)

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60  # Convert to seconds
    )


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT, summary="User logout", description="Logout user by invalidating refresh token")
async def logout(
    response: Response,
    auth_service: AuthService = Depends(get_auth_service),
    user_id: str = Depends(get_current_user_id)
):
    """
    Logout user by invalidating refresh token.

    Args:
        response: FastAPI Response object
        auth_service: AuthService instance
        user_id: ID of the currently authenticated user

    Returns:
        None
    """
    await auth_service.logout(response, user_id)
