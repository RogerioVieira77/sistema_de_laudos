"""
FastAPI Main Application
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.openapi.utils import get_openapi

from app.api.v1 import api_v1_router
from app.core.exceptions import APIException

app = FastAPI(
    title="Sistema de Laudos API",
    description="API para geração de laudos de documentoscopia",
    version="1.0.0",
    docs_url="/api/v1/docs",
    redoc_url="/api/v1/redoc",
    openapi_url="/api/v1/openapi.json",
)

# ============================================================================
# CORS Configuration
# ============================================================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure properly in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# Exception Handlers
# ============================================================================
@app.exception_handler(APIException)
async def api_exception_handler(request, exc: APIException):
    """Global handler for custom API exceptions"""
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )

# ============================================================================
# Include API v1 Routers
# ============================================================================
app.include_router(api_v1_router, prefix="/api/v1")

# ============================================================================
# Root Endpoints
# ============================================================================
@app.get(
    "/",
    tags=["Root"],
    summary="API Root",
    description="Retorna informações da API"
)
def read_root():
    """Root endpoint - returns API information"""
    return {
        "message": "Sistema de Laudos API v1.0.0",
        "status": "running",
        "docs": "/docs",
        "redoc": "/redoc",
    }

@app.get(
    "/api/v1",
    tags=["Root"],
    summary="API v1 Root",
    description="Retorna informações da API v1"
)
def api_root():
    """API v1 root endpoint"""
    return {
        "message": "API v1 is running",
        "version": "1.0.0",
        "endpoints": {
            "health": "/api/v1/health",
            "contratos": "/api/v1/contratos",
            "bureau": "/api/v1/bureau",
            "geolocalizacao": "/api/v1/geolocalizacao",
            "pareceres": "/api/v1/pareceres",
        }
    }

# ============================================================================
# Startup and Shutdown Events
# ============================================================================
@app.on_event("startup")
async def startup_event():
    """Executed when application starts"""
    print("✅ Sistema de Laudos API started")
    print("📚 Docs: http://localhost:8000/docs")
    print("📖 ReDoc: http://localhost:8000/redoc")

@app.on_event("shutdown")
async def shutdown_event():
    """Executed when application shuts down"""
    print("🛑 Sistema de Laudos API shut down")
