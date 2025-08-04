"""
Health check endpoints for monitoring system status.
"""

import logging
from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from app.services.health_check_service import health_service

logger = logging.getLogger(__name__)

router = APIRouter()


class HealthResponse(BaseModel):
    """Response model for health check."""
    status: str
    timestamp: str
    services: Optional[Dict[str, Any]] = None


class ServiceHealthResponse(BaseModel):
    """Response model for individual service health check."""
    service: str
    status: str
    response_time_ms: float
    details: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


@router.get("/", response_model=HealthResponse)
async def health_check(
    details: bool = Query(False, description="Include detailed service status")
) -> HealthResponse:
    """
    Get overall system health status.
    
    This endpoint checks the health of all critical system components:
    - Database connectivity
    - Redis connectivity  
    - Celery worker status
    
    Args:
        details: Whether to include detailed service information
        
    Returns:
        Overall health status with optional service details
        
    Raises:
        HTTPException: If health check fails
    """
    try:
        health_status = await health_service.get_health_status(include_details=details)
        
        # Return 503 if system is unhealthy
        if health_status["status"] == "unhealthy":
            raise HTTPException(
                status_code=503,
                detail="System is unhealthy"
            )
        
        return HealthResponse(**health_status)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Health check failed: {str(e)}"
        )


@router.get("/database", response_model=ServiceHealthResponse)
async def database_health() -> ServiceHealthResponse:
    """
    Check database connectivity and performance.
    
    Returns:
        Database health status with response time
        
    Raises:
        HTTPException: If database check fails
    """
    try:
        health_status = await health_service.get_service_health("database")
        
        if "error" in health_status and health_status["error"] == "service_not_found":
            raise HTTPException(status_code=404, detail=health_status["detail"])
        
        if health_status["status"] == "unhealthy":
            raise HTTPException(
                status_code=503,
                detail=f"Database is unhealthy: {health_status.get('error', 'Unknown error')}"
            )
        
        return ServiceHealthResponse(**health_status)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Database health check failed: {str(e)}"
        )


@router.get("/redis", response_model=ServiceHealthResponse)
async def redis_health() -> ServiceHealthResponse:
    """
    Check Redis connectivity and performance.
    
    Returns:
        Redis health status with response time
        
    Raises:
        HTTPException: If Redis check fails
    """
    try:
        health_status = await health_service.get_service_health("redis")
        
        if "error" in health_status and health_status["error"] == "service_not_found":
            raise HTTPException(status_code=404, detail=health_status["detail"])
        
        if health_status["status"] == "unhealthy":
            raise HTTPException(
                status_code=503,
                detail=f"Redis is unhealthy: {health_status.get('error', 'Unknown error')}"
            )
        
        return ServiceHealthResponse(**health_status)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Redis health check failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Redis health check failed: {str(e)}"
        )


@router.get("/celery", response_model=ServiceHealthResponse)
async def celery_health() -> ServiceHealthResponse:
    """
    Check Celery worker status and availability.
    
    Returns:
        Celery health status with active worker count
        
    Raises:
        HTTPException: If Celery check fails
    """
    try:
        health_status = await health_service.get_service_health("celery")
        
        if "error" in health_status and health_status["error"] == "service_not_found":
            raise HTTPException(status_code=404, detail=health_status["detail"])
        
        if health_status["status"] == "unhealthy":
            raise HTTPException(
                status_code=503,
                detail=f"Celery is unhealthy: {health_status.get('error', 'Unknown error')}"
            )
        
        return ServiceHealthResponse(**health_status)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Celery health check failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Celery health check failed: {str(e)}"
        )


@router.get("/reddit", response_model=ServiceHealthResponse)
async def reddit_api_health() -> ServiceHealthResponse:
    """
    Check Reddit API connectivity and authentication.
    
    Returns:
        Reddit API health status with response time
        
    Raises:
        HTTPException: If Reddit API check fails
    """
    try:
        health_status = await health_service.get_service_health("reddit_api")
        
        if "error" in health_status and health_status["error"] == "service_not_found":
            raise HTTPException(status_code=404, detail=health_status["detail"])
        
        if health_status["status"] == "unhealthy":
            raise HTTPException(
                status_code=503,
                detail=f"Reddit API is unhealthy: {health_status.get('error', 'Unknown error')}"
            )
        
        return ServiceHealthResponse(**health_status)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Reddit API health check failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Reddit API health check failed: {str(e)}"
        )


@router.get("/supabase", response_model=ServiceHealthResponse)
async def supabase_health() -> ServiceHealthResponse:
    """
    Check Supabase connectivity and services.
    
    Returns:
        Supabase health status with response time
        
    Raises:
        HTTPException: If Supabase check fails
    """
    try:
        health_status = await health_service.get_service_health("supabase")
        
        if "error" in health_status and health_status["error"] == "service_not_found":
            raise HTTPException(status_code=404, detail=health_status["detail"])
        
        if health_status["status"] == "unhealthy":
            raise HTTPException(
                status_code=503,
                detail=f"Supabase is unhealthy: {health_status.get('error', 'Unknown error')}"
            )
        
        return ServiceHealthResponse(**health_status)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Supabase health check failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Supabase health check failed: {str(e)}"
        )


@router.get("/ready")
async def readiness_check() -> Dict[str, Any]:
    """
    Kubernetes/Docker readiness probe endpoint.
    
    This is a lightweight check to determine if the service is ready to accept traffic.
    
    Returns:
        Simple ready status
        
    Raises:
        HTTPException: If service is not ready
    """
    try:
        # Quick check of critical services
        health_status = await health_service.get_health_status(include_details=False)
        
        if health_status["status"] == "unhealthy":
            raise HTTPException(status_code=503, detail="Service not ready")
        
        return {
            "status": "ready",
            "timestamp": health_status["timestamp"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        raise HTTPException(
            status_code=503,
            detail="Service not ready"
        )


@router.get("/live")
async def liveness_check() -> Dict[str, str]:
    """
    Kubernetes/Docker liveness probe endpoint.
    
    This is a minimal check to determine if the service is alive.
    
    Returns:
        Simple alive status
    """
    return {
        "status": "alive",
        "service": "reddit-content-platform"
    }