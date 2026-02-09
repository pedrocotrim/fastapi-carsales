"""
Fast Car Sales API - Main Application Entry Point

This module initializes the FastAPI application with all necessary configurations,
middleware, and route handlers for the P2P car dealership platform.
"""

import logging
from typing import Dict
from contextlib import asynccontextmanager
import os

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from routes import profile, seller_application, user, health, auth
from core.exceptions import BaseCustomException
from core.config import settings
from core.database import database_lifespan
from core.redis import redis_lifespan

# Configure logging
log_level = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    level=getattr(logging, log_level),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Initialize FastAPI application


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan handler replacing deprecated on_event startup/shutdown."""
    # Startup actions
    logger.info("Starting Fast Car Sales APIapp..")
    async with redis_lifespan(app):
        async with database_lifespan(app):
            yield  # Yield control to the application
    logger.info("Application shutdown complete")


app = FastAPI(
    title="Fast Car Sales API",
    description="Production-ready P2P car dealership API with FastAPI",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# Handle custom exceptions


@app.exception_handler(BaseCustomException)
async def custom_exception_gandler(request: Request, exc: BaseCustomException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.error,
            "description": exc.description
        },
        headers=exc.headers
    )

# Import routers
# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include route routers with prefixes
app.include_router(auth.router, prefix="/v1")
app.include_router(health.router, prefix="/v1")
app.include_router(user.router, prefix="/v1")
app.include_router(seller_application.router, prefix="/v1")
app.include_router(profile.router, prefix="/v1")

# Root endpoint


@app.get(
    "/",
    status_code=status.HTTP_200_OK,
    tags=["Root"],
    response_model=Dict[str, str],
    summary="Root endpoint",
    description="Returns basic API information"
)
async def root() -> Dict[str, str]:
    """
    Root endpoint providing API welcome message and version.

    Returns:
        Dict[str, str]: Welcome message and API version
    """
    return {
        "message": "Welcome to Fast Car Sales API",
        "version": "0.1.1",
        "docs": "/docs"
    }


# (Startup/shutdown handled by the lifespan manager above)


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc: Exception) -> JSONResponse:
    """
    Handle all unhandled exceptions globally.

    Args:
        request: The request that caused the exception
        exc: The exception that was raised

    Returns:
        JSONResponse: Error response with details
    """
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "Internal server error",
            "message": str(exc)
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
