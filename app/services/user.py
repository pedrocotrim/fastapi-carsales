"""User related domain logic and persistence.

This module provides the UserService class that encapsulates all user-related operations, such as registration, retrieval, and updates.
It interacts with the database using SQLAlchemy's AsyncSession and handles business logic related to users, including validation and error handling.
"""

import logging
from psycopg2 import IntegrityError
from sqlalchemy import select, exists
from sqlalchemy.ext.asyncio import AsyncSession
from slugify import slugify  # type: ignore
import secrets

from core.exceptions import BaseCustomException
from models.user import User, UserRole, Profile
from core.security import hash_password

logger = logging.getLogger(__name__)


class UserService:
    """Handles all user-related operations.
    This is the service responsible for creating, updating and managing user accounts.

    Attributes:
        session (AsyncSession): The database session for performing operations.
    """

    def __init__(self, session: AsyncSession):
        self.session = session

    async def register_user(self,
                            email: str,
                            password: str,
                            full_name: str
                            ) -> User:
        """Registers a new user with the given email, password, and role.

        Args:
            email (str): User's email address
            password (str): User's password
            full_name (str): User's full name

        Raises:
            BaseCustomException: If the email is already in use.

        Returns:
            User: The newly created user object.
        """

        stmt = select(exists()).where(User.email == email)
        existing_user = await self.session.scalars(stmt)

        if existing_user:
            logger.warning(
                f"Registration attempt with existing email: {email}")
            raise BaseCustomException(status_code=409, error="Invalid e-mail",
                                      description="There is already an account with this e-mail address")

        user = User(email=email, role=UserRole.BUYER,
                    password_hash=hash_password(password), is_active=True)
        profile = Profile(user_id=user.id, full_name=full_name)
        user.profile = profile

        MAX_ATTEMPTS = 5
        for _ in range(MAX_ATTEMPTS):
            # Generate username from full name
            username = slugify(full_name, separator="-", strict=True)
            suffix = secrets.token_hex(4)
            profile.slug = f"{username}-{suffix}"

            self.session.add(user)

            try:
                await self.session.commit()
                await self.session.refresh(user)
                await self.session.refresh(profile)
                logger.info(f"User registered: {email}")
                return user
            except IntegrityError as exc:
                logger.warning(
                    f"Failed to register user with email {email}: {exc}")
                await self.session.rollback()
                continue
        raise BaseCustomException(status_code=500, error="Registration failed",
                                  description="Could not generate a unique username. Please try again.")

    async def get_user_by_id(self, user_id: str) -> User:
        """Gets a user by their ID.

        Args:
            user_id (str): The ID of the user to retrieve.

        Raises:
            BaseCustomException: If the user is not found.

        Returns:
            User: The retrieved user object.
        """
        user = await self.session.get(User, user_id)
        if not user:
            logger.warning(f"User not found: {user_id}")
            raise BaseCustomException(status_code=404, error="User not found",
                                      description="The user with the given ID was not found.")
        return user

    async def update_user(
        self,
        user_id: str,
        email: str | None = None,
        role: UserRole | None = None,
        is_active: bool | None = None,
    ) -> User:
        """Updates a user

        Args:
            user_id (str): The ID of the user to update.
            email (str | None, optional): The new email address for the user. Defaults to None.
            role (UserRole | None, optional): The new role for the user. Defaults to None.
            is_active (bool | None, optional): The new active status for the user. Defaults to None.

        Raises:
            BaseCustomException: _description_

        Returns:
            User: _description_
        """

        user = await self.get_user_by_id(user_id)

        if email and email != user.email:
            stmt = select(User).where(User.email == email)
            result = await self.session.scalars(stmt)
            existing = result.first()
            if existing:
                raise BaseCustomException(
                    status_code=409, error="Email already in use", description="The email is already in use.")
            user.email = email

        if role:
            user.role = role

        if is_active is not None:
            user.is_active = is_active

        await self.session.commit()
        await self.session.refresh(user)

        logger.info(f"User updated: {user_id}")
        return user

    async def get_user_by_email(self, email: str) -> User | None:
        """Gets a user by their email address.

        Args:
            email (str): The email address of the user to retrieve.

        Returns:
            User | None: The retrieved user object, or None if not found.
        """
        stmt = select(User).where(User.email == email)
        result = await self.session.scalars(stmt)
        return result.first()

    async def soft_delete_user(self, user_id: str) -> None:
        """Soft deletes a user by the giver user id

        Args:
            user_id (str): User to be deleted
        """
        user = await self.get_user_by_id(user_id)
        user.is_active = False
        await self.session.commit()
        logger.info(f"User soft deleted: {user_id}")
        return None
