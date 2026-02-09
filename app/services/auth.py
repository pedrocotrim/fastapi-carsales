"""Authentication related domain logic and operations.

This module provides the AuthService class that encapsulates all authentication-related operations, such as user login, token generation, and token validation.
It interacts with the database using SQLAlchemy's AsyncSession and handles business logic related to authentication.
"""

import logging
from fastapi import Response
from jose import JWTError, jwt
from redis.asyncio import Redis

from core.security import create_access_token, create_refresh_token, verify_password
from core.exceptions import BaseCustomException
from core.redis import cache_get, cache_set, cache_delete
from core.config import settings
from services.user import UserService
from schema.auth import UserLogin
from models import User

logger = logging.getLogger(__name__)


class AuthService:
    """Service class responsible for authentication-related operations, including user login, token generation, and token validation.

    Attributes:
        user_service (UserService): A UserService object to handle looking for users in the database.
        redis_client (Redis): A Redis client
    """

    def __init__(self, user_service: UserService, redis_client: Redis):
        self.user_service = user_service
        self.redis_client = redis_client

    async def authenticate(self, login_data: UserLogin) -> User:
        """Authenticates a user's login credentials.

        Args:
            email (str): User's email address
            password (str): User's plaintext password

        Raises:
            BaseCustomException: If the email is not found.
            BaseCustomException: If the account is inactive.
            BaseCustomException: If the password is incorrect.

        Returns:
            User: The authenticated user object.
        """
        user = await self.user_service.get_user_by_email(login_data.email)

        if not user:
            logger.warning(
                f"Login attempt with non-existent email: {login_data.email}")
            raise BaseCustomException(status_code=401, error="Invalid email or password",
                                      description="The email or password is incorrect.")
        if not user.is_active:
            logger.warning(
                f"Login attempt on inactive account: {login_data.email}")
            raise BaseCustomException(status_code=401, error="Inactive account",
                                      description="The account is inactive. Please contact support.")

        if not verify_password(login_data.password, user.password_hash):
            logger.warning(
                f"Failed password verification for user: {login_data.email}")
            raise BaseCustomException(status_code=401, error="Invalid email or password",
                                      description="The email or password is incorrect.")

        logger.info(f"User authenticated: {login_data.email}")
        return user

    async def refresh_token(self, response: Response, user_id: str) -> str:
        """Refreshes both the access token and the refresh token.

        Args:
            response (Response): The FastAPI response object to set cookies on.
            user_id (str): The ID of the user whose tokens are being refreshed.

        Returns:
            str: The new access token.
        """

        # Generate token
        access_token = create_access_token(
            user_id, settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        refresh_token = create_refresh_token(
            user_id, settings.REFRESH_TOKEN_EXPIRE_DAYS)
        # Store refresh token in redis cache
        await cache_set(self.redis_client, f"refresh_token:{user_id}", refresh_token, expire=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60)

        # Send refresh token as HttpOnly cookie
        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True)
        return access_token

    async def validate_refresh_token(self, token: str) -> str:
        """Validates a refresh token.

        Args:
            token (str): The refresh token to validate.

        Raises:
            BaseCustomException: If the token is invalid or expired.
            BaseCustomException: If the token type is incorrect.
            BaseCustomException: If the user ID is missing from the token claims.
            BaseCustomException: If the refresh token is revoked or expired.

        Returns:
            str: The user ID extracted from the token claims.
        """
        try:
            # 1. Decode and verify signature
            payload = jwt.decode(
                token,
                settings.JWT_SECRET_KEY.get_secret_value(),
                algorithms=[settings.JWT_ALGORITHM]
            )

            # 2. Check token type claim
            if payload.get("type") != "refresh":
                raise BaseCustomException(
                    status_code=401, error="Invalid token type", description="The refresh token is invalid.")

            user_id = payload.get("sub")
            if not user_id:
                raise BaseCustomException(
                    status_code=401, error="Invalid token claims", description="The refresh token claims are invalid.")

            # 3. Check Redis Whitelist
            # This ensures the token hasn't been revoked/logged out
            stored_token = await cache_get(self.redis_client, f"refresh_token:{user_id}")
            if stored_token != token:
                raise BaseCustomException(status_code=401, error="Token revoked or expired",
                                          description="The refresh token has been revoked or expired.")

            # Making sure the user exists in the database
            _ = await self.user_service.get_user_by_id(user_id)

            return user_id

        except JWTError:
            # Handles expired tokens or tampered signatures
            raise BaseCustomException(
                status_code=401, error="Token expired", description="The refresh token has expired.")

    async def logout(self, response: Response, user_id: str) -> None:
        """Logs user out by deleting the refresh token from the cache and cookie.

        Args:
            response (Response): Response object to delete the cookie
            user_id (str): User id to logout

        Raises:
            BaseCustomException: If refresh token is not found in cache
        """
        logger.info(f"Logging out user {user_id}")
        response.delete_cookie(
            key="refresh_token", httponly=True, secure=True, samesite="strict", path="/")
        deleted = await cache_delete(self.redis_client, f"refresh_token:{user_id}")
        if deleted == 0:
            logger.warning(f"No refresh token for {user_id} in cache")
            raise BaseCustomException(status_code=401, error="Token not found",
                                      description="Refresh token for the given user id was not found")
