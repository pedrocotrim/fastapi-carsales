"""
User models package
"""

from enum import Enum
from sqlalchemy import ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from uuid import UUID

from models.base import Base, SlugMixin, SoftDeleteMixin, TimestampMixin, UUIDMixin


class UserRole(Enum):
    """
    User role enumeration for role-based access control.

    - admin: Full system access, user management
    - seller: Can create and manage car listings
    - buyer: Can browse listings and message sellers
    """
    ADMIN = "admin"
    SELLER = "seller"
    BUYER = "buyer"


class User(Base, TimestampMixin, SoftDeleteMixin, UUIDMixin):
    """
    User account model with authentication and role management.

    Attributes:
        id: Primary key UUID
        email: Unique user email (login credential)
        password_hash: Bcrypt hashed password
        role: User role (admin, seller, buyer)
        is_active: Whether the account is active
        created_at: Account creation timestamp
        updated_at: Last update timestamp
        deleted_at: Soft delete timestamp
    """

    __tablename__ = "users"

    email: Mapped[str] = mapped_column(
        unique=True,
        nullable=False,
        index=True,
        comment="User email address (unique)"
    )

    password_hash: Mapped[str] = mapped_column(
        nullable=False,
        comment="Bcrypt hashed password"
    )

    role: Mapped[UserRole] = mapped_column(
        SQLEnum(UserRole),
        default=UserRole.BUYER,
        nullable=False,
        comment="User role for access control"
    )

    is_active: Mapped[bool] = mapped_column(
        default=True,
        nullable=False,
        comment="Whether the account is active"
    )

    profile: Mapped["Profile"] = relationship(
        "Profile",
        uselist=False,
        back_populates="user",
        cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<User(id={self.id}, email={self.email}, role={self.role})>"


class Profile(Base, TimestampMixin, SlugMixin):
    """
    User profile with personal information and profile picture.

    Fields:
        id: Primary key
        user_id: Reference to User (one-to-one, FK to users.id)
        slug: Unique username used in public URLs
        full_name: User's full name
        phone: Phone number
        city: City of residence
        state: State/province of residence
        country: Country of residence
        picture_filename: UUID filename of stored profile picture (MinIO storage)
        picture_mime: MIME type of stored picture
        created_at: Profile creation timestamp
        updated_at: Last profile update timestamp
    """

    __tablename__ = "profiles"

    id: Mapped[int] = mapped_column(primary_key=True)

    user_id: Mapped[str] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        comment="One-to-one link to User"
    )

    full_name: Mapped[str | None] = mapped_column(
        nullable=True,
        comment="User's full name"
    )

    phone: Mapped[str | None] = mapped_column(
        nullable=True,
        comment="Phone number"
    )

    city: Mapped[str | None] = mapped_column(
        nullable=True,
        comment="City of residence"
    )

    state: Mapped[str | None] = mapped_column(
        nullable=True,
        comment="State/province of residence"
    )

    country: Mapped[str | None] = mapped_column(
        nullable=True,
        comment="Country of residence"
    )

    picture_filename: Mapped[str | None] = mapped_column(
        nullable=True,
        comment="UUID filename of profile picture stored in MinIO"
    )

    picture_mime: Mapped[str | None] = mapped_column(
        nullable=True,
        comment="MIME type of stored picture"
    )

    user = relationship("User", foreign_keys=[user_id])
