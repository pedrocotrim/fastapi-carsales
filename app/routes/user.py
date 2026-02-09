"""
User Routes

Provides endpoints for user management, authentication, and profiles.
"""
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

import logging
from core.dependencies import get_current_user_id, get_user_service
from core.exceptions import BaseCustomException
from services.user import UserService
from schema.user import UserCreate, UserResponse, UserRole

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/users",
    tags=["users"],
    responses={
        404: {"description": "User not found"},
        400: {"description": "Invalid request"}
    }
)


@router.post(
    "register",
    status_code=status.HTTP_201_CREATED,
    summary="Create user",
    description="Create a new user account",
    response_model=UserResponse,
)
async def register(user: UserCreate, user_service: UserService = Depends(get_user_service)) -> UserResponse:
    """
    Create a new user account.

    Args:
        user: The user data to create

    Returns:
        Object with created user details
    """
    created_user = await user_service.register_user(
        email=user.email,
        password=user.password,
        full_name=user.full_name)
    return created_user


@router.delete(
    "",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete user",
    description="Delete a user account"
)
async def delete_user(user_id: str = Depends(get_current_user_id), user_service: UserService = Depends(get_user_service)) -> None:
    """
    Delete a user account.

    Args:
        user_id: The ID of the user to delete
        user_service: UserService dependency
    """
    await user_service.soft_delete_user(user_id)
    return None
