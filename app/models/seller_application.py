"""Seller request model for managing seller role requests."""

from enum import Enum
from datetime import datetime
from sqlalchemy import DateTime, Enum as SQLEnum, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID as PG_UUID

from models.base import Base, TimestampMixin, UUIDMixin


class SellerApplicationStatus(Enum):
    """
    Status for seller role requests.
    """
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class SellerApplication(Base, TimestampMixin, UUIDMixin):
    """
    Seller role request submitted by a user.

    Fields:
        id: Primary key
        user_id: Requesting user (FK to users.id)
        details: Freeform details supplied by user
        status: Request status (pending/approved/rejected)
        reviewed_by: Admin user id who reviewed the request
        admin_notes: Optional notes from reviewer
        reviewed_at: Timestamp when reviewed
    """

    __tablename__ = "seller_applications"

    user_id: Mapped[str] = mapped_column(
        ForeignKey("users.id"), nullable=False, index=True)

    details: Mapped[str] = mapped_column(nullable=False)

    status: Mapped[SellerApplicationStatus] = mapped_column(
        SQLEnum(SellerApplicationStatus),
        default=SellerApplicationStatus.PENDING,
        nullable=False,
        comment="Request status"
    )

    reviewed_by: Mapped[str | None] = mapped_column(
        ForeignKey("users.id"), nullable=True)

    admin_notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    reviewed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True)

    user = relationship("User", foreign_keys=[user_id])
    reviewer = relationship("User", foreign_keys=[reviewed_by])
