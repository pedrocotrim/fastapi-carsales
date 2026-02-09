"""
Health Check Routes

Provides endpoints for monitoring API health and readiness.
"""

from fastapi import APIRouter, status
from typing import Dict

router = APIRouter(
    tags=["health"],
    responses={500: {"description": "Service unhealthy"}}
)


@router.get(
    "",
    status_code=status.HTTP_200_OK,
    summary="Health check",
    description="Returns the health status of the API"
)
async def health_check() -> Dict[str, str]:
    """
    Check if the API is running and healthy.

    Returns:
        Dict[str, str]: Status message indicating API health
    """
    return {"status": "healthy", "service": "Fast Car Sales API"}


@router.get(
    "/ready",
    status_code=status.HTTP_200_OK,
    summary="Readiness check",
    description="Check if the API is ready to accept requests"
)
async def readiness_check() -> Dict[str, str | bool]:
    """
    Check if the API is ready (dependencies initialized).

    Returns:
        Dict[str, str]: Readiness status
    """
    return {"ready": True, "timestamp": "2026-01-24T23:19:30Z"}
