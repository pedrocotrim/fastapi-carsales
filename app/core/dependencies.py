"""Application dependencies for FastAPI.
Provides common dependencies like authentication and authorization.
"""
from typing import Annotated
import logging

from fastapi import Depends, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from jose import JWTError, jwt
from redis.asyncio import Redis

from models.user import UserRole
from services.auth import AuthService
from services.profile import ProfileService
from services.seller_application import SellerApplicationService
from services.user import UserService
from core.exceptions import BaseCustomException, TokenAuthException
from services.storage import StorageService
from models import User
from .database import get_db
from .redis import get_redis
from .config import settings

logger = logging.getLogger(__name__)

# OAuth2 schemes
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


async def get_user_service(db: Annotated[AsyncSession, Depends(get_db)]) -> UserService:
    """Gets a user service object.

    Args:
        db (Annotated[AsyncSession, Depends): Database session dependency

    Returns:
        UserService: UserService instance with database session
    """
    return UserService(db)


async def get_auth_service(user_service: Annotated[UserService, Depends(get_user_service)], redis_client: Annotated[Redis, Depends(get_redis)]) -> AuthService:
    """Gets an authentication service object.

    Args:
        user_service (Annotated[UserService, Depends): UserService dependency
        redis_client (Annotated[Redis, Depends]): Redis dependency

    Returns:
        AuthService: AuthService instance with user service
    """
    return AuthService(user_service, redis_client)


async def get_profile_picture_storage_service() -> StorageService:
    """Gets a Storage Service object that uploads files to the Profile Picture bucket

    Returns:
        StorageService: StorageService instance, acessing the Profile Upload Bucket
    """
    return StorageService(settings.PROFILE_UPLOAD_BUCKET)


async def get_profile_service(session: Annotated[AsyncSession, Depends(get_db)], storage_service: Annotated[StorageService, Depends(get_profile_picture_storage_service)]) -> ProfileService:
    """Gets a profile service object

    Returns:
        ProfileService: ProfileService instance
    """
    return ProfileService(session, storage_service)


async def get_seller_application_service(session: Annotated[AsyncSession, Depends(get_db)]) -> ProfileService:
    """Gets a seller application service object

    Returns:
        SellerApplicationService: SellerApplicationService instance
    """
    return SellerApplicationService(session)


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], user_service: Annotated[UserService, Depends(get_user_service)]) -> User:
    """Get the current authenticated user from the JWT token.

    Args:
        token (str): token to verify

    Raises:
        credentials_exception: If token is invalid or expired
        credentials_exception: If token does not contain required fields

    Returns:
        TokenData: The decoded token data
    """
    credentials_exception = TokenAuthException(
        description="The provided authentication token is invalid or expired.",
    )

    try:
        payload = jwt.decode(
            token, settings.JWT_SECRET_KEY.get_secret_value(), algorithms=[settings.JWT_ALGORITHM])
        user_id: str | None = payload.get("sub")

        if user_id is None:
            raise credentials_exception

        user = await user_service.get_user_by_id(user_id)

        if user.is_active is False:
            raise credentials_exception

        return user

    except JWTError as e:
        logger.warning(f"Invalid token: {e}")
        raise credentials_exception
    except BaseCustomException as e:
        logger.warning(f"Authentication error: {e}")
        raise credentials_exception


async def get_current_user_id(current_user: Annotated[User, Depends(get_current_user)]) -> str:
    return current_user.id


def require_role(*allowed_roles: UserRole):
    """
    Dependency factory to enforce role-based access control.

    Args:
        *allowed_roles: Roles that are allowed to access

    Returns:
        Dependency function that checks user role
    """
    async def role_checker(current_user: User = Depends(get_current_user)) -> User:
        user_role = current_user.role

        if user_role not in allowed_roles:
            logger.warning(
                f"Access denied: user role {user_role} not in allowed roles {allowed_roles}"
            )
            raise BaseCustomException(
                status_code=status.HTTP_403_FORBIDDEN,
                error="Forbidden",
                description=f"This action requires one of these roles: {[r.value for r in allowed_roles]}"
            )

        return current_user

    return role_checker
