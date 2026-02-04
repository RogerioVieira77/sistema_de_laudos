"""
HTTP Exception Handlers for Authentication and Authorization Errors

Provides standardized error responses for common auth/authz failures.
These handlers should be registered with FastAPI app in main.py.

Error Codes:
- 401 Unauthorized: Missing or invalid credentials
- 403 Forbidden: Valid credentials but insufficient permissions
- 429 Too Many Requests: Rate limit exceeded
- 500 Internal Server Error: Unexpected authentication errors
"""

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import HTTPException
import logging
from typing import Union
from datetime import datetime

logger = logging.getLogger(__name__)


class AuthenticationError(HTTPException):
    """Custom exception for authentication failures (401)"""
    def __init__(self, detail: str = "Invalid or expired token"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"},
        )


class AuthorizationError(HTTPException):
    """Custom exception for authorization failures (403)"""
    def __init__(self, detail: str = "Insufficient permissions"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail,
        )


class RateLimitError(HTTPException):
    """Custom exception for rate limit exceeded (429)"""
    def __init__(self, detail: str = "Rate limit exceeded"):
        super().__init__(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=detail,
        )


async def authentication_error_handler(
    request: Request,
    exc: AuthenticationError,
) -> JSONResponse:
    """
    Handler for 401 Unauthorized errors.
    
    Returns standardized JSON response with error details.
    """
    logger.warning(
        f"Authentication error on {request.method} {request.url.path}",
        extra={"detail": exc.detail}
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": "unauthorized",
            "message": exc.detail,
            "status_code": exc.status_code,
            "timestamp": datetime.utcnow().isoformat(),
            "path": request.url.path,
        },
        headers=exc.headers,
    )


async def authorization_error_handler(
    request: Request,
    exc: AuthorizationError,
) -> JSONResponse:
    """
    Handler for 403 Forbidden errors.
    
    Returns standardized JSON response with error details.
    """
    logger.warning(
        f"Authorization error on {request.method} {request.url.path}",
        extra={"detail": exc.detail}
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": "forbidden",
            "message": exc.detail,
            "status_code": exc.status_code,
            "timestamp": datetime.utcnow().isoformat(),
            "path": request.url.path,
        },
    )


async def rate_limit_error_handler(
    request: Request,
    exc: RateLimitError,
) -> JSONResponse:
    """
    Handler for 429 Too Many Requests errors.
    
    Returns standardized JSON response with rate limit info.
    """
    logger.warning(
        f"Rate limit exceeded on {request.method} {request.url.path}",
        extra={"client_host": request.client.host if request.client else "unknown"}
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": "too_many_requests",
            "message": exc.detail,
            "status_code": exc.status_code,
            "timestamp": datetime.utcnow().isoformat(),
            "path": request.url.path,
            "retry_after": 60,  # Suggest retry after 60 seconds
        },
    )


async def http_exception_handler(
    request: Request,
    exc: HTTPException,
) -> JSONResponse:
    """
    Generic HTTP exception handler for all other HTTPException cases.
    
    Standardizes error responses across the API.
    """
    # Don't log successful responses (2xx)
    if exc.status_code >= 400:
        logger.error(
            f"HTTP error {exc.status_code} on {request.method} {request.url.path}",
            extra={
                "status_code": exc.status_code,
                "detail": exc.detail,
                "client": request.client.host if request.client else "unknown",
            }
        )
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": _status_to_error_key(exc.status_code),
            "message": exc.detail,
            "status_code": exc.status_code,
            "timestamp": datetime.utcnow().isoformat(),
            "path": request.url.path,
        },
        headers=getattr(exc, 'headers', None),
    )


async def general_exception_handler(
    request: Request,
    exc: Exception,
) -> JSONResponse:
    """
    Fallback handler for unexpected exceptions.
    
    Logs the error and returns a generic 500 response without exposing details.
    """
    logger.error(
        f"Unexpected error on {request.method} {request.url.path}",
        exc_info=exc,
        extra={
            "client": request.client.host if request.client else "unknown",
        }
    )
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "internal_server_error",
            "message": "An unexpected error occurred",
            "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
            "timestamp": datetime.utcnow().isoformat(),
            "path": request.url.path,
        },
    )


def _status_to_error_key(status_code: int) -> str:
    """Convert HTTP status code to error key for response."""
    status_map = {
        400: "bad_request",
        401: "unauthorized",
        403: "forbidden",
        404: "not_found",
        405: "method_not_allowed",
        409: "conflict",
        422: "unprocessable_entity",
        429: "too_many_requests",
        500: "internal_server_error",
        502: "bad_gateway",
        503: "service_unavailable",
    }
    return status_map.get(status_code, f"http_error_{status_code}")


def register_error_handlers(app: FastAPI) -> None:
    """
    Register all error handlers with FastAPI application.
    
    Call this in main.py after creating the FastAPI app:
    
        app = FastAPI()
        register_error_handlers(app)
    
    Args:
        app: FastAPI application instance
    """
    app.add_exception_handler(AuthenticationError, authentication_error_handler)
    app.add_exception_handler(AuthorizationError, authorization_error_handler)
    app.add_exception_handler(RateLimitError, rate_limit_error_handler)
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(Exception, general_exception_handler)
    
    logger.info("Error handlers registered successfully")
