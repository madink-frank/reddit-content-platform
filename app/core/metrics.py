"""
Prometheus metrics collection and middleware for monitoring.
"""

import time
import psutil
from typing import Callable, Optional
from fastapi import Request, Response
from prometheus_client import (
    Counter, Histogram, Gauge, Info, generate_latest, 
    CONTENT_TYPE_LATEST, CollectorRegistry
)
from prometheus_client.multiprocess import MultiProcessCollector


# Create metrics registry
registry = CollectorRegistry()

# Define metrics
REQUEST_COUNT = Counter(
    'api_requests_total',
    'Total API requests',
    ['method', 'endpoint', 'status_code'],
    registry=registry
)

REQUEST_DURATION = Histogram(
    'api_request_duration_seconds',
    'API request duration in seconds',
    ['method', 'endpoint'],
    buckets=(0.005, 0.01, 0.025, 0.05, 0.075, 0.1, 0.25, 0.5, 0.75, 1.0, 2.5, 5.0, 7.5, 10.0),
    registry=registry
)

REQUEST_SIZE = Histogram(
    'api_request_size_bytes',
    'API request size in bytes',
    ['method', 'endpoint'],
    registry=registry
)

RESPONSE_SIZE = Histogram(
    'api_response_size_bytes',
    'API response size in bytes',
    ['method', 'endpoint'],
    registry=registry
)

# Celery Task Metrics
CELERY_TASK_COUNT = Counter(
    'celery_tasks_total',
    'Total Celery tasks',
    ['task_name', 'status', 'queue'],
    registry=registry
)

CELERY_TASK_DURATION = Histogram(
    'celery_task_duration_seconds',
    'Celery task duration in seconds',
    ['task_name', 'queue'],
    buckets=(0.1, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0, 60.0, 120.0, 300.0, 600.0),
    registry=registry
)

CELERY_TASK_RETRY_COUNT = Counter(
    'celery_task_retries_total',
    'Total Celery task retries',
    ['task_name', 'queue'],
    registry=registry
)

CELERY_ACTIVE_TASKS = Gauge(
    'celery_active_tasks',
    'Number of active Celery tasks',
    ['queue'],
    registry=registry
)

# Business Metrics
CRAWLING_SUCCESS_RATE = Gauge(
    'crawling_success_rate',
    'Reddit crawling success rate (percentage)',
    ['keyword'],
    registry=registry
)

POSTS_CRAWLED = Counter(
    'posts_crawled_total',
    'Total posts crawled from Reddit',
    ['keyword', 'subreddit'],
    registry=registry
)

CONTENT_GENERATED = Counter(
    'content_generated_total',
    'Total content pieces generated',
    ['template_type', 'status'],
    registry=registry
)

TREND_ANALYSIS_COUNT = Counter(
    'trend_analysis_total',
    'Total trend analyses performed',
    ['keyword', 'status'],
    registry=registry
)

# External API Metrics
REDDIT_API_CALLS = Counter(
    'reddit_api_calls_total',
    'Total Reddit API calls',
    ['endpoint', 'status'],
    registry=registry
)

REDDIT_API_RATE_LIMIT = Gauge(
    'reddit_api_rate_limit_remaining',
    'Reddit API rate limit remaining',
    registry=registry
)

REDDIT_API_RESPONSE_TIME = Histogram(
    'reddit_api_response_time_seconds',
    'Reddit API response time in seconds',
    ['endpoint'],
    registry=registry
)

# Database Metrics
DATABASE_CONNECTIONS = Counter(
    'database_connections_total',
    'Total database connections',
    ['status'],
    registry=registry
)

DATABASE_QUERY_DURATION = Histogram(
    'database_query_duration_seconds',
    'Database query duration in seconds',
    ['operation'],
    registry=registry
)

DATABASE_CONNECTION_POOL_SIZE = Gauge(
    'database_connection_pool_size',
    'Database connection pool size',
    registry=registry
)

DATABASE_CONNECTION_POOL_ACTIVE = Gauge(
    'database_connection_pool_active',
    'Active database connections in pool',
    registry=registry
)

# Redis Metrics
REDIS_OPERATIONS = Counter(
    'redis_operations_total',
    'Total Redis operations',
    ['operation', 'status'],
    registry=registry
)

REDIS_RESPONSE_TIME = Histogram(
    'redis_response_time_seconds',
    'Redis operation response time in seconds',
    ['operation'],
    registry=registry
)

REDIS_CACHE_HIT_RATE = Gauge(
    'redis_cache_hit_rate',
    'Redis cache hit rate (percentage)',
    registry=registry
)

REDIS_MEMORY_USAGE = Gauge(
    'redis_memory_usage_bytes',
    'Redis memory usage in bytes',
    registry=registry
)

# System Metrics
SYSTEM_CPU_USAGE = Gauge(
    'system_cpu_usage_percent',
    'System CPU usage percentage',
    registry=registry
)

SYSTEM_MEMORY_USAGE = Gauge(
    'system_memory_usage_bytes',
    'System memory usage in bytes',
    registry=registry
)

SYSTEM_DISK_USAGE = Gauge(
    'system_disk_usage_bytes',
    'System disk usage in bytes',
    ['path'],
    registry=registry
)

# Application Info
APPLICATION_INFO = Info(
    'application_info',
    'Application information',
    registry=registry
)

# Error Metrics
ERROR_COUNT = Counter(
    'errors_total',
    'Total errors by type',
    ['error_type', 'component'],
    registry=registry
)


class PrometheusMiddleware:
    """Enhanced middleware to collect comprehensive Prometheus metrics for HTTP requests."""
    
    def __init__(self):
        pass
    
    async def __call__(self, request: Request, call_next: Callable) -> Response:
        """Process request and collect detailed metrics."""
        start_time = time.time()
        
        # Get endpoint path (normalize dynamic paths)
        endpoint = self._normalize_endpoint(request.url.path)
        method = request.method
        
        # Get request size
        request_size = 0
        if hasattr(request, 'headers') and 'content-length' in request.headers:
            try:
                request_size = int(request.headers['content-length'])
            except (ValueError, TypeError):
                request_size = 0
        
        # Process request
        try:
            response = await call_next(request)
            
            # Calculate duration
            duration = time.time() - start_time
            
            # Get response size
            response_size = 0
            if hasattr(response, 'headers') and 'content-length' in response.headers:
                try:
                    response_size = int(response.headers['content-length'])
                except (ValueError, TypeError):
                    response_size = 0
            
            # Record metrics
            REQUEST_COUNT.labels(
                method=method,
                endpoint=endpoint,
                status_code=response.status_code
            ).inc()
            
            REQUEST_DURATION.labels(
                method=method,
                endpoint=endpoint
            ).observe(duration)
            
            if request_size > 0:
                REQUEST_SIZE.labels(
                    method=method,
                    endpoint=endpoint
                ).observe(request_size)
            
            if response_size > 0:
                RESPONSE_SIZE.labels(
                    method=method,
                    endpoint=endpoint
                ).observe(response_size)
            
            return response
            
        except Exception as e:
            # Record error metrics
            duration = time.time() - start_time
            ERROR_COUNT.labels(
                error_type=type(e).__name__,
                component='api'
            ).inc()
            
            REQUEST_COUNT.labels(
                method=method,
                endpoint=endpoint,
                status_code=500
            ).inc()
            
            REQUEST_DURATION.labels(
                method=method,
                endpoint=endpoint
            ).observe(duration)
            
            raise
    
    def _normalize_endpoint(self, path: str) -> str:
        """Normalize endpoint paths to reduce cardinality."""
        # Replace common dynamic segments with placeholders
        import re
        
        # Replace UUIDs
        path = re.sub(r'/[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}', '/{uuid}', path)
        
        # Replace numeric IDs
        path = re.sub(r'/\d+', '/{id}', path)
        
        # Replace common patterns
        path = re.sub(r'/[a-zA-Z0-9_-]{20,}', '/{token}', path)
        
        return path


def get_metrics_response() -> Response:
    """Generate Prometheus metrics response."""
    try:
        # Try to use multiprocess collector for production
        registry_to_use = CollectorRegistry()
        MultiProcessCollector(registry_to_use)
        metrics_data = generate_latest(registry_to_use)
    except Exception:
        # Fall back to default registry for development
        metrics_data = generate_latest(registry)
    
    return Response(
        content=metrics_data,
        media_type=CONTENT_TYPE_LATEST
    )


# Celery Task Metrics Functions
def record_celery_task_start(task_name: str, queue: str = "default") -> None:
    """Record Celery task start."""
    CELERY_TASK_COUNT.labels(task_name=task_name, status="started", queue=queue).inc()
    CELERY_ACTIVE_TASKS.labels(queue=queue).inc()


def record_celery_task_success(task_name: str, duration: float, queue: str = "default") -> None:
    """Record Celery task success."""
    CELERY_TASK_COUNT.labels(task_name=task_name, status="success", queue=queue).inc()
    CELERY_TASK_DURATION.labels(task_name=task_name, queue=queue).observe(duration)
    CELERY_ACTIVE_TASKS.labels(queue=queue).dec()


def record_celery_task_failure(task_name: str, duration: float, queue: str = "default") -> None:
    """Record Celery task failure."""
    CELERY_TASK_COUNT.labels(task_name=task_name, status="failure", queue=queue).inc()
    CELERY_TASK_DURATION.labels(task_name=task_name, queue=queue).observe(duration)
    CELERY_ACTIVE_TASKS.labels(queue=queue).dec()


def record_celery_task_retry(task_name: str, queue: str = "default") -> None:
    """Record Celery task retry."""
    CELERY_TASK_RETRY_COUNT.labels(task_name=task_name, queue=queue).inc()


# Business Metrics Functions
def record_crawling_success_rate(keyword: str, success_rate: float) -> None:
    """Record crawling success rate for a keyword."""
    CRAWLING_SUCCESS_RATE.labels(keyword=keyword).set(success_rate)


def record_posts_crawled(keyword: str, subreddit: str, count: int = 1) -> None:
    """Record posts crawled."""
    POSTS_CRAWLED.labels(keyword=keyword, subreddit=subreddit).inc(count)


def record_content_generated(template_type: str, status: str) -> None:
    """Record content generation."""
    CONTENT_GENERATED.labels(template_type=template_type, status=status).inc()


def record_trend_analysis(keyword: str, status: str) -> None:
    """Record trend analysis."""
    TREND_ANALYSIS_COUNT.labels(keyword=keyword, status=status).inc()


# External API Metrics Functions
def record_reddit_api_call(endpoint: str, status: str, response_time: Optional[float] = None) -> None:
    """Record Reddit API call with optional response time."""
    REDDIT_API_CALLS.labels(endpoint=endpoint, status=status).inc()
    if response_time is not None:
        REDDIT_API_RESPONSE_TIME.labels(endpoint=endpoint).observe(response_time)


def update_reddit_api_rate_limit(remaining: int) -> None:
    """Update Reddit API rate limit remaining."""
    REDDIT_API_RATE_LIMIT.set(remaining)


# Database Metrics Functions
def record_database_connection(status: str) -> None:
    """Record database connection."""
    DATABASE_CONNECTIONS.labels(status=status).inc()


def record_database_query(operation: str, duration: float) -> None:
    """Record database query duration."""
    DATABASE_QUERY_DURATION.labels(operation=operation).observe(duration)


def update_database_pool_metrics(pool_size: int, active_connections: int) -> None:
    """Update database connection pool metrics."""
    DATABASE_CONNECTION_POOL_SIZE.set(pool_size)
    DATABASE_CONNECTION_POOL_ACTIVE.set(active_connections)


# Redis Metrics Functions
def record_redis_operation(operation: str, status: str, response_time: Optional[float] = None) -> None:
    """Record Redis operation with optional response time."""
    REDIS_OPERATIONS.labels(operation=operation, status=status).inc()
    if response_time is not None:
        REDIS_RESPONSE_TIME.labels(operation=operation).observe(response_time)


def update_redis_cache_hit_rate(hit_rate: float) -> None:
    """Update Redis cache hit rate."""
    REDIS_CACHE_HIT_RATE.set(hit_rate)


def update_redis_memory_usage(memory_bytes: int) -> None:
    """Update Redis memory usage."""
    REDIS_MEMORY_USAGE.set(memory_bytes)


# System Metrics Functions
def update_system_metrics() -> None:
    """Update system metrics (CPU, memory, disk usage)."""
    try:
        # CPU usage
        cpu_percent = psutil.cpu_percent(interval=1)
        SYSTEM_CPU_USAGE.set(cpu_percent)
        
        # Memory usage
        memory = psutil.virtual_memory()
        SYSTEM_MEMORY_USAGE.set(memory.used)
        
        # Disk usage for common paths
        for path in ['/', '/tmp', '/var']:
            try:
                disk = psutil.disk_usage(path)
                SYSTEM_DISK_USAGE.labels(path=path).set(disk.used)
            except (OSError, FileNotFoundError):
                # Path might not exist on all systems
                continue
                
    except Exception as e:
        # Log error but don't fail
        ERROR_COUNT.labels(error_type=type(e).__name__, component='system_metrics').inc()


# Error Metrics Functions
def record_error(error_type: str, component: str) -> None:
    """Record an error occurrence."""
    ERROR_COUNT.labels(error_type=error_type, component=component).inc()


# Application Info Functions
def set_application_info(version: str, environment: str, build_time: str) -> None:
    """Set application information."""
    APPLICATION_INFO.info({
        'version': version,
        'environment': environment,
        'build_time': build_time,
        'python_version': f"{psutil.sys.version_info.major}.{psutil.sys.version_info.minor}.{psutil.sys.version_info.micro}"
    })


def get_current_metrics() -> dict:
    """
    Get current metric values for the monitoring dashboard.
    
    Returns:
        Dictionary containing current metric values
    """
    try:
        # Get current metric values from the registry
        metrics = {}
        
        # Collect samples from all metrics
        for metric_family in registry.collect():
            for sample in metric_family.samples:
                metric_name = sample.name
                metric_value = sample.value
                
                # Map Prometheus metric names to dashboard-friendly names
                if metric_name == 'api_requests_total':
                    metrics['api_requests_total'] = int(metric_value)
                elif metric_name == 'api_request_duration_seconds_sum':
                    # Calculate average response time
                    count_key = 'api_request_duration_seconds_count'
                    if count_key in [s.name for s in metric_family.samples]:
                        count_sample = next(s for s in metric_family.samples if s.name == count_key)
                        if count_sample.value > 0:
                            metrics['api_response_time_avg'] = metric_value / count_sample.value
                        else:
                            metrics['api_response_time_avg'] = 0.0
                elif metric_name == 'celery_tasks_active':
                    metrics['active_tasks'] = int(metric_value)
                elif metric_name == 'database_connections_active':
                    metrics['database_connections'] = int(metric_value)
                elif metric_name == 'redis_memory_usage_bytes':
                    metrics['redis_memory_usage'] = int(metric_value)
                elif metric_name == 'system_cpu_usage_percent':
                    metrics['system_cpu_usage'] = metric_value
                elif metric_name == 'system_memory_usage_percent':
                    metrics['system_memory_usage'] = metric_value
                elif metric_name == 'system_disk_usage_percent':
                    metrics['system_disk_usage'] = metric_value
        
        # Calculate crawling success rate
        crawling_success = 0
        crawling_total = 0
        
        for metric_family in registry.collect():
            for sample in metric_family.samples:
                if sample.name == 'celery_tasks_total':
                    labels = sample.labels or {}
                    if labels.get('task_name', '').startswith('crawling'):
                        crawling_total += sample.value
                        if labels.get('status') == 'success':
                            crawling_success += sample.value
        
        if crawling_total > 0:
            metrics['crawling_success_rate'] = (crawling_success / crawling_total) * 100
        else:
            metrics['crawling_success_rate'] = 0.0
        
        # Set default values for missing metrics
        default_metrics = {
            'api_requests_total': 0,
            'api_response_time_avg': 0.0,
            'active_tasks': 0,
            'database_connections': 0,
            'redis_memory_usage': 0,
            'crawling_success_rate': 0.0,
            'system_cpu_usage': 0.0,
            'system_memory_usage': 0.0,
            'system_disk_usage': 0.0
        }
        
        # Merge with defaults
        for key, default_value in default_metrics.items():
            if key not in metrics:
                metrics[key] = default_value
        
        return metrics
        
    except Exception as e:
        # Return default values if metrics collection fails
        return {
            'api_requests_total': 0,
            'api_response_time_avg': 0.0,
            'active_tasks': 0,
            'database_connections': 0,
            'redis_memory_usage': 0,
            'crawling_success_rate': 0.0,
            'system_cpu_usage': 0.0,
            'system_memory_usage': 0.0,
            'system_disk_usage': 0.0
        }