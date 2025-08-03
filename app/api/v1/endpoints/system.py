"""
System monitoring and metrics endpoints.
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException, Query, Depends
from pydantic import BaseModel

from app.core.dependencies import get_current_user
from app.core.system_metrics import check_database_health, check_redis_health, check_celery_health
from app.core.metrics import get_current_metrics
from app.models.user import User

logger = logging.getLogger(__name__)

router = APIRouter()


class SystemMetrics(BaseModel):
    """System metrics response model."""
    timestamp: str
    api_requests_total: int
    api_response_time_avg: float
    active_tasks: int
    database_connections: int
    redis_memory_usage: int
    crawling_success_rate: float
    system_cpu_usage: float
    system_memory_usage: float
    system_disk_usage: float


class SystemHealth(BaseModel):
    """System health response model."""
    status: str
    timestamp: str
    services: Dict[str, Any]
    overall_health_score: float


class AlertInfo(BaseModel):
    """Alert information model."""
    id: str
    type: str  # 'warning', 'error', 'critical'
    title: str
    message: str
    timestamp: str
    resolved: bool = False


@router.get("/metrics", response_model=List[SystemMetrics])
async def get_system_metrics(
    time_range: str = Query("1h", description="Time range: 1h, 6h, 24h, 7d"),
    current_user: User = Depends(get_current_user)
) -> List[SystemMetrics]:
    """
    Get system metrics for monitoring dashboard.
    
    Args:
        time_range: Time range for metrics (1h, 6h, 24h, 7d)
        current_user: Authenticated user
        
    Returns:
        List of system metrics data points
        
    Raises:
        HTTPException: If metrics collection fails
    """
    try:
        # Get current metrics from Prometheus
        current_metrics = get_current_metrics()
        
        # For now, return current metrics as a single data point
        # In a real implementation, you'd query historical data from Prometheus
        metrics_data = SystemMetrics(
            timestamp=datetime.utcnow().isoformat(),
            api_requests_total=current_metrics.get('api_requests_total', 0),
            api_response_time_avg=current_metrics.get('api_response_time_avg', 0.0),
            active_tasks=current_metrics.get('active_tasks', 0),
            database_connections=current_metrics.get('database_connections', 0),
            redis_memory_usage=current_metrics.get('redis_memory_usage', 0),
            crawling_success_rate=current_metrics.get('crawling_success_rate', 0.0),
            system_cpu_usage=current_metrics.get('system_cpu_usage', 0.0),
            system_memory_usage=current_metrics.get('system_memory_usage', 0.0),
            system_disk_usage=current_metrics.get('system_disk_usage', 0.0)
        )
        
        return [metrics_data]
        
    except Exception as e:
        logger.error(f"Failed to get system metrics: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get system metrics: {str(e)}"
        )


@router.get("/health", response_model=SystemHealth)
async def get_system_health(
    current_user: User = Depends(get_current_user)
) -> SystemHealth:
    """
    Get comprehensive system health status.
    
    Args:
        current_user: Authenticated user
        
    Returns:
        System health status with service details
        
    Raises:
        HTTPException: If health check fails
    """
    try:
        # Check all services
        database_health = await check_database_health()
        redis_health = await check_redis_health()
        celery_health = await check_celery_health()
        
        services = {
            "database": database_health,
            "redis": redis_health,
            "celery": celery_health
        }
        
        # Calculate overall health score
        healthy_services = sum(1 for service in services.values() if service.get('status') == 'healthy')
        total_services = len(services)
        health_score = (healthy_services / total_services) * 100
        
        # Determine overall status
        if health_score == 100:
            overall_status = "healthy"
        elif health_score >= 75:
            overall_status = "degraded"
        else:
            overall_status = "unhealthy"
        
        return SystemHealth(
            status=overall_status,
            timestamp=datetime.utcnow().isoformat(),
            services=services,
            overall_health_score=health_score
        )
        
    except Exception as e:
        logger.error(f"Failed to get system health: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get system health: {str(e)}"
        )


@router.get("/alerts", response_model=List[AlertInfo])
async def get_system_alerts(
    resolved: Optional[bool] = Query(None, description="Filter by resolved status"),
    current_user: User = Depends(get_current_user)
) -> List[AlertInfo]:
    """
    Get system alerts and warnings.
    
    Args:
        resolved: Filter by resolved status (None for all)
        current_user: Authenticated user
        
    Returns:
        List of system alerts
        
    Raises:
        HTTPException: If alert retrieval fails
    """
    try:
        # For now, generate sample alerts based on system health
        alerts = []
        
        # Check system health and generate alerts
        database_health = await check_database_health()
        redis_health = await check_redis_health()
        celery_health = await check_celery_health()
        
        current_time = datetime.utcnow().isoformat()
        
        # Database alerts
        if database_health.get('status') != 'healthy':
            alerts.append(AlertInfo(
                id=f"db_health_{datetime.utcnow().timestamp()}",
                type="error",
                title="Database Health Issue",
                message=f"Database is unhealthy: {database_health.get('error', 'Unknown error')}",
                timestamp=current_time,
                resolved=False
            ))
        
        # Redis alerts
        if redis_health.get('status') != 'healthy':
            alerts.append(AlertInfo(
                id=f"redis_health_{datetime.utcnow().timestamp()}",
                type="error",
                title="Redis Health Issue",
                message=f"Redis is unhealthy: {redis_health.get('error', 'Unknown error')}",
                timestamp=current_time,
                resolved=False
            ))
        
        # Celery alerts
        if celery_health.get('status') != 'healthy':
            alerts.append(AlertInfo(
                id=f"celery_health_{datetime.utcnow().timestamp()}",
                type="warning",
                title="Celery Worker Issue",
                message=f"Celery workers are unhealthy: {celery_health.get('error', 'Unknown error')}",
                timestamp=current_time,
                resolved=False
            ))
        
        # Filter by resolved status if specified
        if resolved is not None:
            alerts = [alert for alert in alerts if alert.resolved == resolved]
        
        return alerts
        
    except Exception as e:
        logger.error(f"Failed to get system alerts: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get system alerts: {str(e)}"
        )


@router.get("/info")
async def get_system_info(
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get system information and configuration.
    
    Args:
        current_user: Authenticated user
        
    Returns:
        System information
        
    Raises:
        HTTPException: If system info retrieval fails
    """
    try:
        from app.core.config import settings
        import platform
        import sys
        
        return {
            "application": {
                "name": "Reddit Content Platform",
                "version": getattr(settings, 'VERSION', '1.0.0'),
                "environment": settings.ENVIRONMENT,
                "debug": getattr(settings, 'DEBUG', False)
            },
            "system": {
                "platform": platform.platform(),
                "python_version": sys.version,
                "architecture": platform.architecture()[0]
            },
            "configuration": {
                "database_url": settings.DATABASE_URL.replace(settings.DATABASE_URL.split('@')[0].split('://')[-1], '***') if '@' in settings.DATABASE_URL else "***",
                "redis_url": settings.REDIS_URL.replace(settings.REDIS_URL.split('@')[0].split('://')[-1], '***') if '@' in settings.REDIS_URL else "***",
                "celery_broker": "configured" if settings.CELERY_BROKER_URL else "not configured"
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to get system info: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get system info: {str(e)}"
        )