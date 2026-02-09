"""
 This module defines custom exceptions for the application.
"""


class BaseCustomException(Exception):
    """Base class for custom exceptions in the application."""

    def __init__(self, status_code: int, error: str, description: str, headers: dict | None = None):
        self.status_code = status_code
        self.error = error
        self.description = description
        self.headers = headers


class TokenAuthException(BaseCustomException):
    """Exception raised for authentication errors."""

    def __init__(self, description: str = "Authentication failed"):
        super().__init__(
            status_code=401,
            error="Authentication Error",
            description=description,
            headers={"WWW-Authenticate": "Bearer"}
        )


class FileUploadException(BaseCustomException):
    """Exception raised for file upload errors."""

    def __init__(self, description: str = "File upload failed"):
        super().__init__(
            status_code=400,
            error="File Upload Error",
            description=description
        )
