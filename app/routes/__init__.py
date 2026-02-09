"""
Routes Package

This package contains all API route modules organized by feature/resource.
Each module defines endpoints for a specific resource using FastAPI's APIRouter.
"""

from typing import List
from .auth import router as auth_router
from .health import router as health_router
from .profile import router as profile_router
from .seller_application import router as seller_application_router
from .user import router as user_router

__all__: List[str] = ["auth_router", "health_router", "profile_router",
                      "seller_application_router", "user_router"]
