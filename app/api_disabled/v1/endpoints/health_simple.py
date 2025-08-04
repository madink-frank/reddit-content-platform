"""
Simplified health check endpoints for Vercel deployment.
"""

from fastapi import APIRouter
from datetime import datetime
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/")
async def health_check():
    """Basic health check."""
    return {
        "status": "healthy",
        "service": "reddit-content-platform",
        "timestamp": datetime.utcnow().isoformat(),
        "version": settings.VERSION
    }

@router.get("/basic")
async def basic_health():
    """Basic health check with minimal information."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat()
    }

@router.get("/config")
async def config_health():
    """Check if basic configuration is loaded."""
    try:
        return {
            "status": "healthy",
            "config": {
                "project_name": settings.PROJECT_NAME,
                "version": settings.VERSION,
                "environment": settings.ENVIRONMENT,
                "api_prefix": settings.API_V1_STR,
                "supabase_configured": bool(settings.SUPABASE_URL),
                "database_configured": bool(settings.DATABASE_URL)
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Config health check failed: {e}")
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }

@router.get("/supabase")
async def supabase_health():
    """Check Supabase configuration."""
    try:
        if not settings.SUPABASE_URL:
            return {
                "status": "not_configured",
                "message": "SUPABASE_URL not set",
                "timestamp": datetime.utcnow().isoformat()
            }
        
        if not settings.SUPABASE_ANON_KEY:
            return {
                "status": "not_configured", 
                "message": "SUPABASE_ANON_KEY not set",
                "timestamp": datetime.utcnow().isoformat()
            }
        
        return {
            "status": "configured",
            "supabase_url": settings.SUPABASE_URL[:50] + "..." if len(settings.SUPABASE_URL) > 50 else settings.SUPABASE_URL,
            "has_anon_key": bool(settings.SUPABASE_ANON_KEY),
            "has_service_key": bool(settings.SUPABASE_SERVICE_ROLE_KEY),
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Supabase health check failed: {e}")
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }