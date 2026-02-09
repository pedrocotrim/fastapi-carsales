"""Application core utilities and configurations."""

from typing import List

from .config import settings
from .database import get_db
from .dependencies import get_user_service, get_auth_service, get_current_user, require_role
from .exceptions import BaseCustomException, TokenAuthException
from .redis import get_redis, cache_set, cache_get, cache_delete
from .security import create_access_token, create_refresh_token, verify_password, hash_password

__all__: List[str] = ["settings", "get_db", "get_user_service", "get_auth_service", "get_current_user", "require_role", "BaseCustomException",
                      "TokenAuthException", "get_redis", "cache_set", "cache_get", "cache_delete", "create_access_token", "create_refresh_token",
                      "verify_password", "hash_password"]
