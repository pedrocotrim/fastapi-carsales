"""
Redis Cache Configuration and Utilities

This module handles Redis connection and provides caching utilities
for the application.
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator, Any, Optional

from fastapi import FastAPI, Request
import redis.asyncio as redis
from core.config import settings
import logging
import json


logger = logging.getLogger(__name__)


@asynccontextmanager
async def redis_lifespan(app: FastAPI) -> AsyncGenerator[redis.Redis, None]:
    """Lifespan handler for Redis connection."""
    client = await redis.from_url(
        str(settings.REDIS_URL),
        encoding="utf-8",
        decode_responses=True,
        retry_on_timeout=True,
        max_connections=10
    )
    try:
        # Test connection
        await client.ping()
        logger.info("Redis connection established successfully")
        app.state.redis = client
        yield client
    finally:
        await client.close()
        logger.info("Redis connection closed")


def get_redis(request: Request) -> redis.Redis:
    """Gets redis client from app state.

    Args:
        request (Request): Request object to access app state

    Returns:
        redis.Redis: Redis client instance
    """
    if not hasattr(request.app.state, "redis"):
        raise RuntimeError(
            "Redis client not initialized. Please ensure Redis is properly configured and initialized.")
    return request.app.state.redis


async def cache_set(
    client: redis.Redis,
    key: str,
    value: Any,
    expire: int = 3600
) -> bool:
    """
    Set a value in cache with expiration.

    Args:
        client: Redis client instance
        key: Cache key
        value: Value to cache (will be JSON serialized)
        expire: Expiration time in seconds (default: 1 hour)

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        serialized_value = json.dumps(value)
        await client.setex(key, expire, serialized_value)
        return True
    except Exception as e:
        logger.error(f"Cache set error for key {key}: {e}")
        return False


async def cache_get(client: redis.Redis, key: str) -> Optional[Any]:
    """
    Get a value from cache.

    Args:
        client: Redis client instance
        key: Cache key

    Returns:
        Cached value (JSON deserialized) or None if not found
    """
    try:
        value = await client.get(key)
        if value:
            return json.loads(value)
        return None
    except Exception as e:
        logger.error(f"Cache get error for key {key}: {e}")
        return None


async def cache_delete(client: redis.Redis, key: str) -> bool:
    """
    Delete a value from cache.

    Args:
        client: Redis client instance
        key: Cache key

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        await client.delete(key)
        return True
    except Exception as e:
        logger.error(f"Cache delete error for key {key}: {e}")
        return False
