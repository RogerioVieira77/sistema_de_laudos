"""
Health Check Router
Simple endpoint to verify API and dependencies are working
"""

from fastapi import APIRouter, Depends
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.api.dependencies import get_db

router = APIRouter(
    prefix="/health",
    tags=["Health Check"],
)


@router.get("", tags=["Health Check"])
async def health_check(db: Session = Depends(get_db)):
    """
    Health check endpoint - verifies API and database connectivity.
    
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
