"""
User Pydantic Schemas

Request/response validation models for user authentication and management.
"""

from pydantic import EmailStr, Field
from datetime import datetime
from models import UserRole

from schema.base import BaseSchema


class UserCreate(BaseSchema):
    """
    Schema for user registration request.

    Attributes:
        email: User email address
        password: Plaintext password (min 8 chars, will be hashed)
    """
    email: EmailStr = Field(description="User email address")
    password: str = Field(
        min_length=8,
        max_length=128,
        description="Password (min 8 characters)"
    )
    full_name: str = Field(
        max_length=100,
        description="User's full name"
    )


class UserResponse(BaseSchema):
    """
    Schema for user response (safe to return to client).

    Never includes password_hash in responses.
    """
    id: int
    email: str
    role: UserRole
    is_active: bool
    created_at: datetime
    updated_at: datetime


class UserUpdate(BaseSchema):
    """
    Schema for updating user information.

    All fields optional - only provided fields will be updated.
    """
    email: EmailStr | None = Field(None, description="New email address")
    role: UserRole | None = Field(
        None, description="New user role (admin only)")
    is_active: bool | None = Field(
        None, description="Account active status (admin only)")
