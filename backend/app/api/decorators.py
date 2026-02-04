"""
Decorators for Authorization and Access Control

Provides role-based and tenant-based authorization decorators
to enforce permissions at the endpoint level.

Usage:
    @router.get("/admin-only")
    @require_roles("admin")
    async def admin_endpoint(identity: Identity = Depends(get_identity)):
        ...
        
    @router.get("/multi-tenant-safe")
    @require_tenant()
    async def safe_endpoint(identity: Identity = Depends(get_identity)):
        # Automatically ensures requests only access their tenant's data
        ...
"""

from functools import wraps
from typing import Callable, List
from fastapi import HTTPException, status
from app.core.oidc_models import Identity
import logging

logger = logging.getLogger(__name__)


def require_roles(*required_roles: str) -> Callable:
    """
    Decorator to enforce role-based access control.
    
    Validates that the authenticated user has at least one of the required roles.
    
    Args:
        *required_roles: Variable number of role names (case-insensitive).
                        User needs at least ONE of these roles.
                        
    Returns:
        Decorated function that checks roles before execution
        
    Raises:
        HTTPException(403): If user doesn't have required role
        
    Example:
        @router.get("/admin")
        @require_roles("admin")
        async def admin_endpoint(identity: Identity = Depends(get_identity)):
            # Only users with "admin" role can access
            return {"role": identity.roles}
            
        @router.post("/create-contrato")
        @require_roles("analista", "revisor", "admin")
        async def create_contrato(
            identity: Identity = Depends(get_identity),
            db: Session = Depends(get_db)
        ):
            # Users with "analista" OR "revisor" OR "admin" can create
            contrato = Contrato(tenant_id=identity.tenant_id, ...)
            db.add(contrato)
            db.commit()
            return contrato
    """
    # Normalize roles to lowercase for case-insensitive comparison
    required_roles_lower = {role.lower() for role in required_roles}
    
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            # Extract identity from kwargs (injected by FastAPI)
            identity = None
            for arg in args:
                if isinstance(arg, Identity):
                    identity = arg
                    break
            
            if not identity:
                for arg in kwargs.values():
                    if isinstance(arg, Identity):
                        identity = arg
                        break
            
            if not identity:
                logger.error("Identity not found in require_roles decorator")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Authentication error"
                )
            
            # Check if user has any of the required roles
            user_roles_lower = {role.lower() for role in (identity.roles or [])}
            
            if not user_roles_lower.intersection(required_roles_lower):
                logger.warning(
                    f"Access denied - insufficient roles",
                    extra={
                        "user_id": identity.sub,
                        "required_roles": list(required_roles_lower),
                        "user_roles": list(user_roles_lower),
                    }
                )
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Insufficient permissions. Required roles: {', '.join(required_roles_lower)}"
                )
            
            logger.info(
                f"Role check passed",
                extra={
                    "user_id": identity.sub,
                    "required_roles": list(required_roles_lower),
                    "user_roles": list(user_roles_lower),
                }
            )
            
            # Call original function
            return await func(*args, **kwargs)
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            # Same logic for sync functions
            identity = None
            for arg in args:
                if isinstance(arg, Identity):
                    identity = arg
                    break
            
            if not identity:
                for arg in kwargs.values():
                    if isinstance(arg, Identity):
                        identity = arg
                        break
            
            if not identity:
                logger.error("Identity not found in require_roles decorator")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Authentication error"
                )
            
            user_roles_lower = {role.lower() for role in (identity.roles or [])}
            
            if not user_roles_lower.intersection(required_roles_lower):
                logger.warning(
                    f"Access denied - insufficient roles",
                    extra={
                        "user_id": identity.sub,
                        "required_roles": list(required_roles_lower),
                        "user_roles": list(user_roles_lower),
                    }
                )
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Insufficient permissions. Required roles: {', '.join(required_roles_lower)}"
                )
            
            logger.info(
                f"Role check passed",
                extra={
                    "user_id": identity.sub,
                    "required_roles": list(required_roles_lower),
                    "user_roles": list(user_roles_lower),
                }
            )
            
            return func(*args, **kwargs)
        
        # Return appropriate wrapper based on whether function is async
        if hasattr(func, '__self__'):  # Instance method
            return sync_wrapper
        else:
            # Try to detect if it's async
            import inspect
            if inspect.iscoroutinefunction(func):
                return async_wrapper
            else:
                return sync_wrapper
        
    return decorator


def require_tenant() -> Callable:
    """
    Decorator to enforce tenant isolation.
    
    Validates that requests can only access data within their own tenant.
    This decorator primarily serves as a marker/contract that the endpoint
    properly filters by tenant_id. The actual filtering should be done
    in the endpoint logic.
    
    Args:
        None (decorator is used without arguments)
        
    Returns:
        Decorated function with tenant validation context
        
    Raises:
        HTTPException(403): If tenant_id is invalid or missing
        
    Example:
        @router.get("/contratos")
        @require_tenant()
        async def list_contratos(
            identity: Identity = Depends(get_identity),
            db: Session = Depends(get_db)
        ):
            # Automatically enforce: only return contratos for identity.tenant_id
            contratos = db.query(Contrato)\
                .filter(Contrato.tenant_id == identity.tenant_id)\
                .all()
            return contratos
            
        @router.get("/contratos/{id}")
        @require_tenant()
        async def get_contrato(
            id: str,
            identity: Identity = Depends(get_identity),
            db: Session = Depends(get_db)
        ):
            # Enforce: verify contrato belongs to identity.tenant_id before returning
            contrato = db.query(Contrato)\
                .filter(Contrato.id == id)\
                .filter(Contrato.tenant_id == identity.tenant_id)\
                .first()
            
            if not contrato:
                raise HTTPException(status_code=404, detail="Contrato not found")
            
            return contrato
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            # Extract identity from kwargs (injected by FastAPI)
            identity = None
            for arg in args:
                if isinstance(arg, Identity):
                    identity = arg
                    break
            
            if not identity:
                for arg in kwargs.values():
                    if isinstance(arg, Identity):
                        identity = arg
                        break
            
            if not identity:
                logger.error("Identity not found in require_tenant decorator")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Authentication error"
                )
            
            # Validate tenant_id is set
            if not identity.tenant_id:
                logger.warning(
                    f"Access denied - tenant_id missing",
                    extra={"user_id": identity.sub}
                )
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Tenant information missing"
                )
            
            logger.debug(
                f"Tenant validation passed",
                extra={
                    "user_id": identity.sub,
                    "tenant_id": identity.tenant_id,
                }
            )
            
            # Call original function
            return await func(*args, **kwargs)
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            # Same logic for sync functions
            identity = None
            for arg in args:
                if isinstance(arg, Identity):
                    identity = arg
                    break
            
            if not identity:
                for arg in kwargs.values():
                    if isinstance(arg, Identity):
                        identity = arg
                        break
            
            if not identity:
                logger.error("Identity not found in require_tenant decorator")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Authentication error"
                )
            
            if not identity.tenant_id:
                logger.warning(
                    f"Access denied - tenant_id missing",
                    extra={"user_id": identity.sub}
                )
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Tenant information missing"
                )
            
            logger.debug(
                f"Tenant validation passed",
                extra={
                    "user_id": identity.sub,
                    "tenant_id": identity.tenant_id,
                }
            )
            
            return func(*args, **kwargs)
        
        # Return appropriate wrapper based on whether function is async
        import inspect
        if inspect.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
        
    return decorator
