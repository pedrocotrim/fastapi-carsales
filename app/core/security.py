"""Security utility functions."""
import bcrypt
from datetime import datetime, timedelta, timezone
from typing import Optional
import logging
from jose import jwt

from core.config import settings

logger = logging.getLogger(__name__)


def hash_password(password: str) -> str:
    """
    Hash a plaintext password using bcrypt.

    Args:
        password: Plaintext password to hash

    Returns:
        str: Bcrypt hashed password
    """
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")


def verify_password(password: str, hashed: str) -> bool:
    """
    Verify a plaintext password against the stored hash.

    Args:
        password: Plaintext password to verify
        hashed: Bcrypt hashed password

    Returns:
        bool: True if password matches, False otherwise
    """
    return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))


def create_access_token(user_id: str, expires_delta: Optional[timedelta] = None) -> str:
    """Generates a JWT access token.

    Args:
        user_id (str): ID of the user
        expires_delta (Optional[timedelta], optional): Token expiration delta. If None, uses default settings.

    Returns:
        str: The generated JWT access token.
    """
    if expires_delta is None:
        expires_delta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    expire = datetime.now(timezone.utc) + expires_delta

    to_encode = {
        "sub": str(user_id),  # Subject (user ID)
        "exp": expire,        # Expiration time
        "iat": datetime.now(timezone.utc),  # Issued at
        "type": "access"
    }

    encoded_jwt = jwt.encode(
        to_encode, settings.JWT_SECRET_KEY.get_secret_value(), algorithm=settings.JWT_ALGORITHM)
    logger.debug(f"Access token created for user {user_id}")

    return encoded_jwt


def create_refresh_token(user_id: int, expires_delta: Optional[timedelta] = None) -> str:
    """Generates a JWT refresh token.

    Args:
        user_id (str): ID of the user
        expires_delta (Optional[timedelta], optional): Token expiration delta. If None, uses default settings.

    Returns:
        str: The generated JWT refresh token.
    """
    if expires_delta is None:
        expires_delta = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

    expire = datetime.now(timezone.utc) + expires_delta

    to_encode = {
        "sub": str(user_id),  # Subject (user ID)
        "exp": expire,        # Expiration time
        "iat": datetime.now(timezone.utc),  # Issued at
        "type": "refresh"
    }

    encoded_jwt = jwt.encode(
        to_encode, settings.JWT_SECRET_KEY.get_secret_value(), algorithm=settings.JWT_ALGORITHM)
    logger.debug(f"Refresh token created for user {user_id}")

    return encoded_jwt
