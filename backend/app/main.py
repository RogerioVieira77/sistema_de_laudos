"""
FastAPI Main Application
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

app = FastAPI(
    title="Sistema de Laudos API",
    description="API para geração de laudos de documentoscopia",
    version="1.0.0"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure properly in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Sistema de Laudos API v1.0.0"}

@app.get("/api/v1/health")
def health_check():
    return {
        "status": "healthy",
        "service": "Sistema de Laudos Backend",
        "version": "1.0.0"
    }

@app.get("/api/v1")
def api_root():
    return {"message": "API v1 is running"}
