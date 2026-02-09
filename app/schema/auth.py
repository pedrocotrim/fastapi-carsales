"""Authorization and Authentication Schemas."""

from pydantic import EmailStr, Field
from schema.base import BaseSchema

class UserLogin(BaseSchema):
    """
    Schema for user login request.

    Attributes:
        email: User email address
        password: Plaintext password
    """
    email: EmailStr = Field(description="User email address")
    password: str = Field(description="User password")

class TokenResponse(BaseSchema):
    """
    Schema for authentication token response.

    Attributes:
        access_token: JWT access token
        token_type: Type of the token (e.g., Bearer)
    """
    access_token: str = Field(description="JWT access token")
    token_type: str = Field(default="bearer", description="Type of the token")

class TokenData(BaseSchema):
    """
    Schema for token data (used in JWT payload).

    Attributes:
        email: User email address
        user_id: Unique identifier for the user
    """
    user_id: str = Field(description="Unique identifier for the user")