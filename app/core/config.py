"""Application configuration and settings management."""

from typing import Any
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import PostgresDsn, RedisDsn, SecretStr, field_validator


class Settings(BaseSettings):
    DATABASE_URL: PostgresDsn

    REDIS_URL: RedisDsn

    # Environment Settings
    ENVIRONMENT: str = "development"

    # Authentication Settings
    JWT_SECRET_KEY: SecretStr
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # CORS Settings
    CORS_ORIGINS: Any = []

    # Email Settings
    # SMTP_HOST: str
    # SMTP_PORT: int = 587
    # SMTP_USER: str
    # SMTP_PASSWORD: SecretStr
    # EMAIL_FROM: EmailStr
    # EMAIL_FROM_NAME: str = "CarSales Support"
    # EMAIL_STARTTLS: bool = True
    # EMAIL_SSL: bool = False
    # EMAIL_USE_CREDENTIALS: bool = True

    # File Upload Settings
    MAX_UPLOAD_SIZE: int = 5 * 1024 * 1024  # 5 MB
    ALLOWED_IMAGE_MIMES: Any = ["image/jpeg", "image/png"]
    PROFILE_UPLOAD_BUCKET: str = "profile"

    # MinIO Settings
    MINIO_PORT: int = 9000
    MINIO_ROOT_USER: str
    MINIO_ROOT_PASSWORD: SecretStr
    MINIO_ENDPOINT: str
    MINIO_ACCESS_KEY: SecretStr
    MINIO_SECRET_KEY: SecretStr
    MINIO_USE_SSL: bool = False
    CDN_BASE_URL: str

    # Clamd Settings
    CLAMD_HOST: str
    CLAMD_PORT: int = 3310

    # Varnish Cache Settings
    VARNISH_URL: str

    # Logging Settings
    LOG_LEVEL: str = "INFO"

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v) -> list[str] | str:
        if isinstance(v, str) and not v.startswith("["):
            # Split by comma and strip whitespace
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    @field_validator("ALLOWED_IMAGE_MIMES", mode="before")
    @classmethod
    def assemble_allowed_image_mimes(cls, v):
        if isinstance(v, str):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, list):
            return v
        raise ValueError(v)

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra='ignore')


settings = Settings()  # type: ignore
