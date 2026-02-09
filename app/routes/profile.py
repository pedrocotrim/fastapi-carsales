"""
Profile management API endpoints.
"""

import logging
from fastapi import APIRouter, Depends, UploadFile, File

from core.dependencies import get_current_user, get_profile_service
from models.user import User
from schema.profile import ProfileUpdateResponse, ProfileUpdate, ProfilePictureResponse
from services.profile import ProfileService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/profiles",
                   tags=["profiles"], responses={404: {"description": "Not found"}})


@router.put("/", response_model=ProfileUpdateResponse)
async def update_profile(
    body: ProfileUpdate,
    user: User = Depends(get_current_user),
    profile_service: ProfileService = Depends(get_profile_service)
) -> ProfileUpdateResponse:
    """Updates the profile for the current user

    Args:
        body (ProfileUpdate): Request body
        user (User, optional): Dependency that gets the current user. Defaults to Depends(get_current_user).
        profile_service (ProfileService, optional): Dependency that provides a profile service. Defaults to Depends(get_profile_service).

    Returns:
        ProfileUpdateResponse: The updated profile response
    """
    profile = await profile_service.update_profile(profile_update=body, user_id=user.id)
    return profile


@router.post("/picture", response_model=ProfilePictureResponse)
async def upload_profile_picture(
    file: UploadFile = File(...),
    user: User = Depends(get_current_user),
    profile_service: ProfileService = Depends(get_profile_service)
):
    """Uploads a profile picture for the current user

    Args:
        file (UploadFile): The uploaded image file
        user (User, optional): Dependency that gets the current user. Defaults to Depends(get_current_user).
        profile_service (ProfileService, optional): Dependency that provides a profile service. Defaults to Depends(get_profile_service).

    Returns:
        ProfilePictureResponse: The uploaded profile picture response
    """
    picture_response = await profile_service.upload_picture(file, user.id)
    return picture_response
