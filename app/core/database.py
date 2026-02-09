"""
Database Configuration and Session Management

This module handles database connection, session management, and provides
dependency injection functions for FastAPI endpoints.
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator
from fastapi import FastAPI
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    AsyncEngine,
    create_async_engine,
    async_sessionmaker
)
from sqlalchemy.pool import NullPool
from core.config import settings
import logging
from functools import lru_cache

logger = logging.getLogger(__name__)

# Create async engine


@lru_cache(maxsize=1)
def get_engine() -> AsyncEngine:
    return create_async_engine(
        settings.DATABASE_URL.unicode_string(),
        echo=True if settings.ENVIRONMENT == "development" else False,
        future=True,
        pool_pre_ping=True,
        poolclass=NullPool if settings.ENVIRONMENT == "testing" else None,
        pool_size=20,
        max_overflow=10,
        pool_timeout=30,
        pool_recycle=3600,
    )


# Async session factory
@lru_cache(maxsize=1)
def get_sessionmaker() -> async_sessionmaker:
    return async_sessionmaker(
        get_engine(),
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False
    )


@asynccontextmanager
async def database_lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Lifespan handler to initialize and close database connections.

    This function is used in FastAPI's lifespan to ensure that the database
    engine and sessionmaker are properly initialized on startup and disposed on shutdown.
    """
    logger.info("Initializing database connection")
    get_sessionmaker()

    try:
        yield
    finally:
        logger.info("Disposing database connection")
        engine = get_engine()
        await engine.dispose()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency function to get database session for FastAPI endpoints.

    Yields:
        AsyncSession: Database session that will be automatically closed

    Example:
        @get("/users")
        async def get_users(db: AsyncSession = Depends(get_db)):
            # Use db session here
            pass
    """
    session = get_sessionmaker()()
    try:
        yield session
    except Exception as e:
        await session.rollback()
        logger.error(f"Database session error: {e}")
        raise
    finally:
        await session.close()
