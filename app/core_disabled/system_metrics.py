"""
System metrics collection for monitoring system resources.
"""

import asyncio
import logging
from typing import Dict, Any
import psutil
import redis
from sqlalchemy import text
from app.core.config import settings
from app.core.database import get_db
from app.core.redis_client import redis_client
from app.core.metrics import (
    update_system_metrics, update_redis_memory_usage,
    update_database_pool_metrics, record_error,
    set_application_info
)

logger = logging.getLogger(__name__)


class SystemMetricsCollector:
    """Collects and updates system metrics periodically."""
    
    def __init__(self):
        self.redis_client = None
        self.db_session = None
        self._running = False
    
    async def start(self, interval: int = 30):
        """Start collecting metrics at specified interval (seconds)."""
        self._running = True
        
        # Set application info once
        try:
            set_application_info(
                version=settings.VERSION,
                environment=settings.ENVIRONMENT,
                build_time="unknown"  # Could be set from build process
            )
        except Exception as e:
            logger.error(f"Failed to set application info: {e}")
        
        while self._running:
            try:
                await self.collect_all_metrics()
                await asyncio.sleep(interval)
            except Exception as e:
                logger.error(f"Error collecting system metrics: {e}")
                record_error(type(e).__name__, 'system_metrics_collector')
                await asyncio.sleep(interval)
    
    def stop(self):
        """Stop collecting metrics."""
        self._running = False
    
    async def collect_all_metrics(self):
        """Collect all system metrics."""
        await asyncio.gather(
            self.collect_system_metrics(),
            self.collect_redis_metrics(),
            self.collect_database_metrics(),
            return_exceptions=True
        )
    
    async def collect_system_metrics(self):
        """Collect basic system metrics."""
        try:
            update_system_metrics()
        except Exception as e:
            logger.error(f"Failed to collect system metrics: {e}")
            record_error(type(e).__name__, 'system_metrics')
    
    async def collect_redis_metrics(self):
        """Collect Redis metrics."""
        try:
            if not self.redis_client:
                self.redis_client = await redis_client.get_async_client()
            
            # Get Redis info
            info = await self.redis_client.info('memory')
            memory_usage = info.get('used_memory', 0)
            update_redis_memory_usage(memory_usage)
            
            # Test Redis connectivity
            await self.redis_client.ping()
            
        except Exception as e:
            logger.error(f"Failed to collect Redis metrics: {e}")
            record_error(type(e).__name__, 'redis_metrics')
    
    async def collect_database_metrics(self):
        """Collect database metrics."""
        try:
            # Get database session
            db_gen = get_db()
            db = next(db_gen)
            
            try:
                # Test database connectivity
                result = db.execute(text("SELECT 1"))
                
                # Get connection pool info (if available)
                if hasattr(db.bind, 'pool'):
                    pool = db.bind.pool
                    pool_size = pool.size()
                    active_connections = pool.checkedout()
                    update_database_pool_metrics(pool_size, active_connections)
                
            finally:
                db.close()
                
        except Exception as e:
            logger.error(f"Failed to collect database metrics: {e}")
            record_error(type(e).__name__, 'database_metrics')


# Global metrics collector instance
metrics_collector = SystemMetricsCollector()


async def start_metrics_collection(interval: int = 30):
    """Start the metrics collection process."""
    logger.info(f"Starting system metrics collection with {interval}s interval")
    await metrics_collector.start(interval)


def stop_metrics_collection():
    """Stop the metrics collection process."""
    logger.info("Stopping system metrics collection")
    metrics_collector.stop()


# Health check functions that also update metrics
async def check_redis_health() -> Dict[str, Any]:
    """Check Redis health and update metrics."""
    try:
        redis_client_instance = await redis_client.get_async_client()
        start_time = asyncio.get_event_loop().time()
        
        await redis_client_instance.ping()
        
        response_time = asyncio.get_event_loop().time() - start_time
        
        # Record metrics
        from app.core.metrics import record_redis_operation
        record_redis_operation('ping', 'success', response_time)
        
        return {
            'status': 'healthy',
            'response_time_ms': round(response_time * 1000, 2)
        }
        
    except Exception as e:
        from app.core.metrics import record_redis_operation
        record_redis_operation('ping', 'failure')
        record_error(type(e).__name__, 'redis_health_check')
        
        return {
            'status': 'unhealthy',
            'error': str(e)
        }


async def check_database_health() -> Dict[str, Any]:
    """Check database health and update metrics."""
    try:
        db_gen = get_db()
        db = next(db_gen)
        
        start_time = asyncio.get_event_loop().time()
        
        try:
            db.execute(text("SELECT 1"))
            response_time = asyncio.get_event_loop().time() - start_time
            
            # Record metrics
            from app.core.metrics import record_database_query, record_database_connection
            record_database_query('health_check', response_time)
            record_database_connection('success')
            
            return {
                'status': 'healthy',
                'response_time_ms': round(response_time * 1000, 2)
            }
            
        finally:
            db.close()
            
    except Exception as e:
        from app.core.metrics import record_database_connection
        record_database_connection('failure')
        record_error(type(e).__name__, 'database_health_check')
        
        return {
            'status': 'unhealthy',
            'error': str(e)
        }


async def check_celery_health() -> Dict[str, Any]:
    """Check Celery health and update metrics."""
    try:
        from app.core.celery_app import celery_app
        
        # Get active workers
        inspect = celery_app.control.inspect()
        active_workers = inspect.active()
        
        if active_workers:
            worker_count = len(active_workers)
            return {
                'status': 'healthy',
                'active_workers': worker_count,
                'workers': list(active_workers.keys())
            }
        else:
            return {
                'status': 'unhealthy',
                'error': 'No active workers found'
            }
            
    except Exception as e:
        record_error(type(e).__name__, 'celery_health_check')
        return {
            'status': 'unhealthy',
            'error': str(e)
        }