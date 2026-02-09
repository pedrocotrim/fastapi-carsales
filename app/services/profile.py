"""Profile business logic service.

Handles profile updates and secure image upload/storage.
"""

import logging
from uuid import UUID

from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from core.exceptions import BaseCustomException

from .storage import StorageService
from schema.profile import ProfileUpdate, ProfileUpdateResponse, ProfilePictureResponse
from models import Profile


logger = logging.getLogger(__name__)


class ProfileService:
    """Service for profile management and image handling.
        Attributes:
            session (AsyncSession): The database session for performing operations.
            redis_client (redis.Redis): The Redis client for caching.
            storage_service (StorageService): The service for handling file storage operations.
    """

    def __init__(self, session: AsyncSession, storage_service: StorageService):
        self.session = session
        self.storage_service = storage_service

    async def update_profile(self, profile_update: ProfileUpdate, user_id: UUID) -> ProfileUpdateResponse:
        """Update user profile information.

        Args:
            profile_update (ProfileUpdate): The profile update data.
            user_id (UUID): The ID of the user whose profile is being updated.

        Returns:
            ProfileUpdateResponse: The updated profile information.
        """
        stmt = select(Profile).where(Profile.user_id == user_id)
        result = await self.session.scalars(stmt)
        profile = result.first()

        if not profile:
            raise BaseCustomException(status_code=404, detail="Profile not found",
                                      message=f"Profile not found for user_id: {user_id}")

        update_dict = profile_update.model_dump(
            exclude_unset=True, exclude_none=True)

        if not update_dict:
            raise BaseCustomException(status_code=400, detail="No valid fields to update",
                                      message="At least one field must be provided for update")
        for key, value in update_dict.items():
            setattr(profile, key, value)

        self.session.add(profile)
        await self.session.commit()
        await self.session.refresh(profile)
        return ProfileUpdateResponse(profile)

    async def upload_picture(self, picture: UploadFile, user_id: UUID) -> ProfilePictureResponse:
        stmt = select(Profile).where(Profile.user_id == user_id)
        result = await self.session.scalars(stmt)
        profile = result.first()
        if profile.picture_filename:
            self.storage_service.delete_file(profile.picture_filename)
        picture_mime, picture_name = await self.storage_service.upload_image(picture, self.storage_service.bucket_name)

        profile.picture_filename = picture_name
        profile.picture_mime = picture_mime

        await self.session.commit()

        return ProfilePictureResponse(self.storage_service.get_presigned_url(picture_name))
