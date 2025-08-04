"""
Health check service for monitoring system components.
"""

import time
from datetime import datetime
from typing import Dict, Any, Optional
from sqlalchemy import text
from app.core.database import SessionLocal
from app.core.redis_client import redis_client
from app.core.celery_app import celery_app
from app.services.reddit_service import reddit_client
from app.core.supabase_client import supabase_manager


class HealthCheckService:
    """Service for checking health of system components."""
    
    async def get_health_status(self, include_details: bool = False) -> Dict[str, Any]:
        """Get overall health status of all components."""
        services = {
            "database": await self._check_database(),
            "redis": await self._check_redis(),
            "celery": await self._check_celery(),
            "reddit_api": await self._check_reddit_api(),
            "supabase": await self._check_supabase()
        }
        
        # Determine overall status (ignore unavailable services)
        critical_services = ["database", "redis", "celery"]
        overall_status = "healthy" if all(
            services[service]["status"] == "healthy" 
            for service in critical_services
            if service in services
        ) else "unhealthy"
        
        result = {
            "status": overall_status,
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }
        
        if include_details:
            result["services"] = services
        
        return result
    
    async def get_service_health(self, service_name: str) -> Dict[str, Any]:
        """Get health status of a specific service."""
        service_checks = {
            "database": self._check_database,
            "redis": self._check_redis,
            "celery": self._check_celery,
            "reddit_api": self._check_reddit_api,
            "supabase": self._check_supabase
        }
        
        if service_name not in service_checks:
            return {
                "error": "service_not_found",
                "detail": f"Service '{service_name}' not found"
            }
        
        check_func = service_checks[service_name]
        result = await check_func()
        result["service"] = service_name
        
        return result
    
    async def _check_database(self) -> Dict[str, Any]:
        """Check database connectivity and performance."""
        start_time = time.time()
        
        try:
            db = SessionLocal()
            try:
                # Simple query to test connection
                db.execute(text("SELECT 1"))
                response_time = (time.time() - start_time) * 1000  # Convert to ms
                
                return {
                    "status": "healthy",
                    "response_time_ms": round(response_time, 2),
                    "details": {
                        "connection_pool": "active"
                    }
                }
            finally:
                db.close()
                
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            return {
                "status": "unhealthy",
                "response_time_ms": round(response_time, 2),
                "error": str(e)
            }
    
    async def _check_redis(self) -> Dict[str, Any]:
        """Check Redis connectivity and performance."""
        start_time = time.time()
        
        try:
            # Test Redis connection
            ping_result = await redis_client.ping()
            response_time = (time.time() - start_time) * 1000  # Convert to ms
            
            if ping_result:
                return {
                    "status": "healthy",
                    "response_time_ms": round(response_time, 2),
                    "details": {
                        "connection": "active"
                    }
                }
            else:
                return {
                    "status": "unhealthy",
                    "response_time_ms": round(response_time, 2),
                    "error": "Redis ping failed"
                }
                
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            return {
                "status": "unhealthy",
                "response_time_ms": round(response_time, 2),
                "error": str(e)
            }
    
    async def _check_celery(self) -> Dict[str, Any]:
        """Check Celery worker status."""
        start_time = time.time()
        
        try:
            # Check active workers
            inspect = celery_app.control.inspect()
            active_workers = inspect.active()
            response_time = (time.time() - start_time) * 1000  # Convert to ms
            
            if active_workers:
                worker_count = len(active_workers)
                return {
                    "status": "healthy",
                    "response_time_ms": round(response_time, 2),
                    "active_workers": worker_count,
                    "details": {
                        "workers": list(active_workers.keys())
                    }
                }
            else:
                return {
                    "status": "unhealthy",
                    "response_time_ms": round(response_time, 2),
                    "active_workers": 0,
                    "error": "No active Celery workers found"
                }
                
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            return {
                "status": "unhealthy",
                "response_time_ms": round(response_time, 2),
                "active_workers": 0,
                "error": str(e)
            }
    
    async def _check_reddit_api(self) -> Dict[str, Any]:
        """Check Reddit API connectivity and authentication."""
        start_time = time.time()
        
        try:
            # Use the existing Reddit client health check
            health_status = await reddit_client.health_check()
            response_time = (time.time() - start_time) * 1000  # Convert to ms
            
            return {
                "status": health_status["status"],
                "response_time_ms": round(response_time, 2),
                "details": {
                    "message": health_status["message"],
                    "timestamp": health_status["timestamp"]
                }
            }
            
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            return {
                "status": "unhealthy",
                "response_time_ms": round(response_time, 2),
                "error": str(e)
            }
    
    async def _check_supabase(self) -> Dict[str, Any]:
        """Check Supabase connectivity and services."""
        start_time = time.time()
        
        try:
            # Use the Supabase manager health check
            health_status = await supabase_manager.health_check()
            response_time = (time.time() - start_time) * 1000  # Convert to ms
            
            return {
                "status": health_status["status"],
                "response_time_ms": round(response_time, 2),
                "details": {
                    "message": health_status["message"]
                },
                "error": health_status.get("error")
            }
            
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            return {
                "status": "unhealthy",
                "response_time_ms": round(response_time, 2),
                "error": str(e)
            }


# Global health check service instance
health_service = HealthCheckService()