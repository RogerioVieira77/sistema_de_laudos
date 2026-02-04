"""
API v1 Router Registration
Aggregates and exports all v1 endpoints
"""

from fastapi import APIRouter

from .health import router as health_router
from .contratos import router as contratos_router
from .bureau import router as bureau_router
from .geolocalizacao import router as geolocalizacao_router
from .pareceres import router as pareceres_router
from .audit_logs import router as audit_logs_router

# Create main API v1 router
api_v1_router = APIRouter()

# Include all sub-routers
api_v1_router.include_router(health_router)
api_v1_router.include_router(contratos_router)
api_v1_router.include_router(bureau_router)
api_v1_router.include_router(geolocalizacao_router)
api_v1_router.include_router(pareceres_router)
api_v1_router.include_router(audit_logs_router)

__all__ = ["api_v1_router"]
