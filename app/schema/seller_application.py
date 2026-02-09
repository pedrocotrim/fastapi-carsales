from datetime import datetime
from enum import Enum
from pydantic import Field
from typing import Optional

from schema.base import BaseSchema


class SellerApplicationStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class SellerApplicationCreate(BaseSchema):
    details: str = Field(None, description="Details for seller application")


class SellerApplicationResponse(BaseSchema):
    id: int
    user_id: int
    details: Optional[str]
    status: SellerApplicationStatus
    admin_notes: Optional[str]
    reviewed_by: Optional[int]
    reviewed_at: Optional[datetime]
    created_at: datetime


class SellerApplicationShow(BaseSchema):
    id: int
    user_id: str
    details: Optional[str]
    status: SellerApplicationStatus
    admin_notes: Optional[str]
    reviewed_by: Optional[str]
    reviewed_at: Optional[datetime]
    created_at: datetime


class SellerApplicationReview(BaseSchema):
    status: SellerApplicationStatus
    admin_notes: str = Field(
        None, description="Optional notes from the admin reviewing the application")
