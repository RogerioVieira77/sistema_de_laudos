"""
FastAPI Dependency Injection - Authentication, Authorization, Database

Provides:
- get_db: Database session injection (SessionLocal)
- get_identity: JWT token validation, returns Identity (authenticated user)
- get_current_user: Alias for get_identity (semantic clarity)
- get_optional_identity: Optional authentication (returns Identity or None)
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Generator, Optional
import os
import logging

from app.models.database import SessionLocal
from app.core import get_provider
from app.core.oidc_models import Identity
from app.services.audit_log_service import AuditLogService

logger = logging.getLogger(__name__)

# Security scheme for Swagger/OpenAPI documentation
security = HTTPBearer(
    description="Bearer token for authentication (JWT from OIDC provider)"
)


def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency for database session injection.
    
    Yields SessionLocal instance and ensures proper cleanup on completion.
    
    Usage:
        @router.get("/items")
        def get_items(db: Session = Depends(get_db)):
            return db.query(Item).all()
    """
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        db.rollback()
        logger.error(f"Database error: {str(e)}", exc_info=True)
        raise
    finally:
        db.close()


async def get_identity(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> Identity:
    """
    FastAPI dependency to extract and validate JWT token.
    
    Extracts Bearer token from Authorization header, validates against OIDC provider,
    and returns normalized Identity object with user context.
    
    Validation Steps:
    1. Extract Bearer token from HTTP Authorization header
    2. Validate token signature against JWKS (from IdP)
    3. Validate token claims (exp, aud, iss)
    4. Normalize claims to Identity (handles different IdPs via IdentityAdapter)
    5. Return Identity with user context (sub, email, roles, tenant_id, etc)
    
    Args:
        credentials: HTTPAuthorizationCredentials from Bearer scheme
        
    Returns:
        Identity: Validated and normalized user identity
        
    Raises:
        HTTPException(401): If token missing, invalid, expired, or signature mismatch
        HTTPException(401): If claims validation fails (audience, issuer, expiration)
        
    Example:
        @router.get("/contratos")
        async def list_contratos(identity: Identity = Depends(get_identity)):
            # User is authenticated and authorized
            # identity.sub, identity.email, identity.roles, identity.tenant_id
            contratos = db.query(Contrato)\
                .filter(Contrato.tenant_id == identity.tenant_id)\
                .all()
            return contratos
    """
    if not credentials:
        logger.warning("Missing credentials in Authorization header")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token = credentials.credentials
    
    try:
        # Get configured OIDC provider (singleton across request)
        provider = await get_provider()
        
        # Validate token signature and claims against IdP metadata
        result = await provider.validate_token(
            token=token,
            expected_aud="laudos-api"
        )
        
        # Check if validation was successful
        if not result.valid:
            logger.warning(
                f"Token validation failed: {result.error}",
                extra={"error_code": result.error_code}
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=result.error or "Invalid token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Validation succeeded, should always have identity
        if not result.identity:
            logger.error("Token validated but no identity returned (programming error)")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        identity = result.identity
        
        # Log successful authentication
        logger.info(
            f"User authenticated",
            extra={
                "user_id": identity.sub,
                "email": identity.email,
                "tenant_id": identity.tenant_id,
                "roles": identity.roles,
            }
        )
        
        return identity
        
    except HTTPException:
        # Re-raise FastAPI exceptions (already properly formatted)
        raise
    except Exception as e:
        logger.error(
            f"Unexpected error during token validation: {str(e)}",
            exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token validation error",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user(
    identity: Identity = Depends(get_identity),
) -> Identity:
    """
    Semantic alias for get_identity().
    
    Use this when you want to express "I need the current authenticated user"
    rather than "I need the identity". Functionally identical to get_identity.
    
    Example:
        @router.get("/profile")
        async def get_profile(user: Identity = Depends(get_current_user)):
            return user.to_dict()
    """
    return identity


async def get_optional_identity(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(
        HTTPBearer(auto_error=False)
    ),
) -> Optional[Identity]:
    """
    Optional identity dependency for public endpoints supporting authentication.
    
    Does NOT raise 401 if credentials missing. Returns None if no token,
    returns Identity if valid token provided.
    
    Use for endpoints that are public but can be personalized if authenticated
    (e.g., "show me public data, or personalized data if authenticated").
    
    Args:
        credentials: Optional HTTPAuthorizationCredentials (auto_error=False)
        
    Returns:
        Identity if valid token provided, None if no credentials or invalid token
        
    Example:
        @router.get("/public-data")
        async def get_public_data(
            identity: Optional[Identity] = Depends(get_optional_identity)
        ):
            base_data = {"status": "public"}
            if identity:
                base_data["personalized"] = True
                base_data["user_email"] = identity.email
            return base_data
    """
    if not credentials:
        return None
    
    try:
        provider = await get_provider()
        
        # Validate token, don't log as warning if invalid (it's optional)
        result = await provider.validate_token(
            token=credentials.credentials,
            expected_aud="laudos-api"
        )
        
        if result.valid and result.identity:
            logger.debug(
                f"Optional authentication succeeded",
                extra={"email": result.identity.email}
            )
            return result.identity
        
        logger.debug("Optional token validation failed, treating as unauthenticated")
        return None
        
    except Exception as e:
        logger.debug(f"Optional token validation error (treating as public): {str(e)}")
        return None


def get_audit_log_service(db: Session = Depends(get_db)) -> AuditLogService:
    """
    FastAPI dependency for AuditLog service injection.
    
    Provides service for logging and querying audit trail.
    
    Usage:
        @router.get("/audit-logs")
        def get_logs(service: AuditLogService = Depends(get_audit_log_service)):
            return service.get_user_activity(user_id)
    """
    return AuditLogService(db)
