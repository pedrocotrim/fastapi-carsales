"""
Pydantic schemas for user profiles.
"""

from pydantic import Field
from typing import Optional
from datetime import datetime

from schema.base import BaseSchema


class ProfileUpdate(BaseSchema):
    """Schema for updating a profile (excluding picture)."""
    full_name: Optional[str] = Field(None, max_length=255)
    phone: Optional[str] = Field(None, max_length=20)
    city: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, max_length=100)
    country: Optional[str] = Field(None, max_length=100)


class ProfilePictureResponse(BaseSchema):
    """Response indicating picture upload success or failure."""
    picture_url: Optional[str] = Field(
        None, description="CDN URL of uploaded picture on success")


class ProfileResponse(BaseSchema):
    """Full profile response."""
    username: str
    full_name: Optional[str] = None
    phone: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    picture_filename: Optional[str] = None
    picture_mime: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class ProfileUpdateResponse(BaseSchema):
    """Response from profile update with picture upload status."""
    profile: ProfileResponse
    image_upload: str = Field(
        description="'success', 'skipped' (no image provided), or 'failed: <reason>'"
    )
    image_url: Optional[str] = Field(
        None, description="CDN URL of new picture if successful")
