"""
API Package - Contains all API endpoints, dependencies, decorators, and error handlers

Key Modules:
- dependencies: FastAPI dependency injection (get_identity, get_db, optional auth)
- decorators: Authorization decorators (@require_roles, @require_tenant)
- error_handlers: Standardized error responses (401, 403, 429, 500)
"""

from .dependencies import (
    get_db,
    get_identity,
    get_current_user,
    get_optional_identity,
    security,
)
from .decorators import require_roles, require_tenant
from .error_handlers import (
    AuthenticationError,
    AuthorizationError,
    RateLimitError,
    register_error_handlers,
)
from .v1 import api_v1_router

__all__ = [
    # Dependencies
    "get_db",
    "get_identity",
    "get_current_user",
    "get_optional_identity",
    "security",
    # Decorators
    "require_roles",
    "require_tenant",
    # Error Handlers
    "AuthenticationError",
    "AuthorizationError",
    "RateLimitError",
    "register_error_handlers",
    # Routers
    "api_v1_router",
]
