"""
Minimal FastAPI application for Vercel deployment.
This version has no external dependencies and should work in serverless environment.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from datetime import datetime
import os

# Create FastAPI app with minimal configuration
app = FastAPI(
    title="Reddit Content Platform API",
    version="1.0.0",
    description="Reddit Content Crawling and Trend Analysis Platform - Minimal Version",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for now
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Reddit Content Platform API - Minimal Version",
        "version": "1.0.0",
        "status": "running",
        "timestamp": datetime.utcnow().isoformat(),
        "docs": "/docs",
        "endpoints": {
            "health": "/health",
            "api_v1": "/api/v1/",
            "config": "/config"
        }
    }

@app.get("/health")
async def health_check():
    """Basic health check endpoint."""
    return {
        "status": "healthy",
        "service": "reddit-content-platform-minimal",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
        "environment": os.getenv("ENVIRONMENT", "production")
    }

@app.get("/config")
async def config_check():
    """Check basic configuration."""
    return {
        "status": "healthy",
        "config": {
            "supabase_url_configured": bool(os.getenv("SUPABASE_URL")),
            "database_url_configured": bool(os.getenv("DATABASE_URL")),
            "jwt_secret_configured": bool(os.getenv("JWT_SECRET_KEY")),
            "environment": os.getenv("ENVIRONMENT", "production"),
            "project_name": os.getenv("PROJECT_NAME", "Reddit Content Platform")
        },
        "timestamp": datetime.utcnow().isoformat()
    }

# API v1 routes
@app.get("/api/v1/")
async def api_v1_root():
    """API v1 root endpoint."""
    return {
        "message": "Reddit Content Platform API v1 - Minimal Version",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat(),
        "available_endpoints": [
            "/api/v1/health",
            "/api/v1/status"
        ]
    }

@app.get("/api/v1/health")
async def api_v1_health():
    """API v1 health check."""
    return {
        "status": "healthy",
        "api_version": "v1",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "reddit-content-platform-minimal"
    }

@app.get("/api/v1/status")
async def api_v1_status():
    """API v1 status endpoint."""
    return {
        "status": "operational",
        "api_version": "v1",
        "timestamp": datetime.utcnow().isoformat(),
        "features": {
            "authentication": "not_implemented",
            "keywords": "not_implemented", 
            "crawling": "not_implemented",
            "trends": "not_implemented"
        },
        "message": "This is a minimal version for deployment testing. Full features will be added incrementally."
    }

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler for better error reporting."""
    return JSONResponse(
        status_code=500,
        content={
            "error": "internal_server_error",
            "message": "An internal server error occurred",
            "timestamp": datetime.utcnow().isoformat(),
            "detail": str(exc) if os.getenv("ENVIRONMENT") == "development" else "Internal server error"
        }
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)