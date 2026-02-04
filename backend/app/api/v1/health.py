"""
Health Check Router
Simple endpoint to verify API and dependencies are working

This router provides a public health check endpoint that does not require authentication.
Used for uptime monitoring and load balancer health probes.

Rate Limiting: UNLIMITED (no rate limit for health checks)
"""

from fastapi import APIRouter, Depends, Request
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.api.dependencies import get_db
from app.api.rate_limiting import limiter, RateLimits

router = APIRouter(
    prefix="/health",
    tags=["Health Check"],
)


@router.get("", tags=["Health Check"])
@limiter.limit(RateLimits.UNLIMITED)
async def health_check(request: Request, db: Session = Depends(get_db)):
    """
    Health check endpoint - verifies API and database connectivity.
    
    **Note**: This endpoint does NOT require authentication.
    It is intended for uptime monitoring and load balancer probes.
    
    **Rate Limit**: UNLIMITED (no rate limiting)
    
    Returns:
        JSON with status, timestamp, and component statuses
        
    Example:
        GET /api/v1/health
        
        Response:
        {
            "status": "OK",
            "timestamp": "2024-02-02T10:50:00.123456Z",
            "service": "Sistema de Laudos Backend",
            "version": "1.0.0",
            "components": {
                "api": "UP",
                "database": "UP"
            }
        }
    """
    
    database_status = "DOWN"
    
    try:
        # Test database connection with a simple query
        db.execute(text("SELECT 1"))
        database_status = "UP"
    except Exception as e:
        database_status = f"DOWN - {str(e)}"
    
    return {
        "status": "OK" if database_status == "UP" else "DEGRADED",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "service": "Sistema de Laudos Backend",
        "version": "1.0.0",
        "components": {
            "api": "UP",
            "database": database_status,
        }
    }
