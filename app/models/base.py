"""
Base ORM Model Definition

This module contains the base SQLAlchemy declarative base and common mixins
that will be inherited by all database models.
"""

from datetime import datetime
import uuid
from sqlalchemy import DateTime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.sql import func


class Base(DeclarativeBase):
    """
    Base class for all SQLAlchemy models.

    All models should inherit from this class to be properly registered
    with SQLAlchemy's declarative system.
    """
    pass


class TimestampMixin:
    """
    Mixin that adds timestamp fields to models.

    Attributes:
        created_at: Timestamp when the record was created
        updated_at: Timestamp when the record was last updated
    """

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )


class SoftDeleteMixin:
    """
    Mixin that adds soft delete functionality to models.

    Attributes:
        deleted_at: Timestamp when the record was soft deleted (NULL if active)
    """

    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        default=None
    )

    def soft_delete(self) -> None:
        """Mark this record as deleted without removing it from the database."""
        self.deleted_at = datetime.now()

    def restore(self) -> None:
        """Restore a soft-deleted record."""
        self.deleted_at = None

    @property
    def is_deleted(self) -> bool:
        """Check if this record has been soft deleted."""
        return self.deleted_at is not None


class UUIDMixin:
    """
    Mixin that adds a UUID primary key to models.

    Attributes:
        id: UUID primary key
    """

    id: Mapped[str] = mapped_column(
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        unique=True,
        nullable=False,
    )


class SlugMixin:
    """
    Mixin that adds a slug field to models.

    Attributes:
        slug: URL-friendly unique identifier
    """

    slug: Mapped[str] = mapped_column(
        unique=True,
        nullable=False,
        index=True,
        comment="URL-friendly unique identifier"
    )
