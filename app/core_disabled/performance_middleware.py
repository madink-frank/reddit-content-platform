"""
Performance optimization middleware for FastAPI.
"""

import time
import asyncio
import logging
from typing import Callable, Dict, Any
from datetime import datetime
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.base import RequestResponseEndpoint
from starlette.responses import JSONResponse

from app.core.metrics import REQUEST_DURATION, REQUEST_COUNT

logger = logging.getLogger(__name__)


class PerformanceMiddleware(BaseHTTPMiddleware):
    """Middleware for performance monitoring and optimization."""
    
    def __init__(self, app: FastAPI, slow_request_threshold: float = 1.0):
        super().__init__(app)
        self.slow_request_threshold = slow_request_threshold
        self.request_stats = {}
    
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        start_time = time.time()
        
        # Add request ID for tracing
        request_id = f"{int(time.time() * 1000)}-{id(request)}"
        request.state.request_id = request_id
        
        try:
            # Process request
            response = await call_next(request)
            
            # Calculate response time
            process_time = time.time() - start_time
            
            # Add performance headers
            response.headers["X-Process-Time"] = str(process_time)
            response.headers["X-Request-ID"] = request_id
            
            # Log slow requests
            if process_time > self.slow_request_threshold:
                logger.warning(
                    f"Slow request detected: {process_time:.3f}s - "
                    f"{request.method} {request.url.path}"
                )
            
            # Update request statistics
            self._update_request_stats(request, process_time, response.status_code)
            
            # Update metrics
            REQUEST_DURATION.labels(
                method=request.method, 
                endpoint=request.url.path
            ).observe(process_time)
            REQUEST_COUNT.labels(
                method=request.method,
                endpoint=request.url.path,
                status_code=response.status_code
            ).inc()
            
            return response
            
        except Exception as e:
            process_time = time.time() - start_time
            logger.error(f"Request error after {process_time:.3f}s: {str(e)}")
            
            # Update error metrics
            REQUEST_DURATION.labels(
                method=request.method, 
                endpoint=request.url.path
            ).observe(process_time)
            REQUEST_COUNT.labels(
                method=request.method,
                endpoint=request.url.path,
                status_code=500
            ).inc()
            
            raise
    
    def _update_request_stats(self, request: Request, process_time: float, status_code: int):
        """Update request statistics."""
        endpoint = f"{request.method} {request.url.path}"
        
        if endpoint not in self.request_stats:
            self.request_stats[endpoint] = {
                "count": 0,
                "total_time": 0.0,
                "avg_time": 0.0,
                "min_time": float('inf'),
                "max_time": 0.0,
                "error_count": 0
            }
        
        stats = self.request_stats[endpoint]
        stats["count"] += 1
        stats["total_time"] += process_time
        stats["avg_time"] = stats["total_time"] / stats["count"]
        stats["min_time"] = min(stats["min_time"], process_time)
        stats["max_time"] = max(stats["max_time"], process_time)
        
        if status_code >= 400:
            stats["error_count"] += 1
    
    def get_performance_report(self) -> Dict[str, Any]:
        """Get performance report."""
        return {
            "request_stats": self.request_stats,
            "slow_requests": [
                {
                    "endpoint": endpoint,
                    "avg_time": stats["avg_time"],
                    "max_time": stats["max_time"],
                    "count": stats["count"]
                }
                for endpoint, stats in self.request_stats.items()
                if stats["avg_time"] > self.slow_request_threshold
            ]
        }


class ResponseCompressionMiddleware(BaseHTTPMiddleware):
    """Middleware for response compression."""
    
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        response = await call_next(request)
        
        # Add compression headers for large responses
        if hasattr(response, 'body') and len(response.body) > 1024:  # 1KB threshold
            response.headers["Content-Encoding"] = "gzip"
        
        return response


class CacheMiddleware(BaseHTTPMiddleware):
    """Middleware for response caching."""
    
    def __init__(self, app: FastAPI, cache_ttl: int = 300):
        super().__init__(app)
        self.cache_ttl = cache_ttl
        self.cacheable_methods = {"GET"}
        self.cacheable_paths = {
            "/api/v1/posts",
            "/api/v1/trends",
            "/api/v1/keywords",
            "/api/v1/public-blog"
        }
    
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        # Only cache GET requests for specific paths
        if (request.method not in self.cacheable_methods or 
            not any(request.url.path.startswith(path) for path in self.cacheable_paths)):
            return await call_next(request)
        
        # Generate cache key
        cache_key = self._generate_cache_key(request)
        
        # For now, just pass through without caching
        # TODO: Implement proper caching when cache modules are available
        response = await call_next(request)
        
        return response
    
    def _generate_cache_key(self, request: Request) -> str:
        """Generate cache key for request."""
        # Include path, query parameters, and user context
        key_parts = [
            request.url.path,
            str(sorted(request.query_params.items())),
            getattr(request.state, 'user_id', 'anonymous')
        ]
        
        import hashlib
        key_string = ":".join(str(part) for part in key_parts)
        key_hash = hashlib.md5(key_string.encode()).hexdigest()
        
        return f"response_cache:{key_hash}"


class DatabaseConnectionMiddleware(BaseHTTPMiddleware):
    """Middleware for database connection optimization."""
    
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        # Set database session timeout for the request
        request.state.db_timeout = 30  # 30 seconds
        
        try:
            response = await call_next(request)
            return response
        except Exception as e:
            # Log database-related errors
            if "database" in str(e).lower() or "connection" in str(e).lower():
                logger.error(f"Database connection error: {e}")
            raise


class RateLimitingMiddleware(BaseHTTPMiddleware):
    """Simple rate limiting middleware."""
    
    def __init__(self, app: FastAPI, requests_per_minute: int = 60):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.request_counts = {}
        self.window_size = 60  # 1 minute window
    
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        client_ip = request.client.host
        current_time = int(time.time())
        window_start = current_time - (current_time % self.window_size)
        
        # Clean old entries
        self.request_counts = {
            key: count for key, count in self.request_counts.items()
            if key[1] >= window_start
        }
        
        # Check rate limit
        key = (client_ip, window_start)
        current_count = self.request_counts.get(key, 0)
        
        if current_count >= self.requests_per_minute:
            return JSONResponse(
                status_code=429,
                content={"detail": "Rate limit exceeded"},
                headers={"Retry-After": str(self.window_size)}
            )
        
        # Update count
        self.request_counts[key] = current_count + 1
        
        # Add rate limit headers
        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(self.requests_per_minute)
        response.headers["X-RateLimit-Remaining"] = str(
            self.requests_per_minute - self.request_counts[key]
        )
        response.headers["X-RateLimit-Reset"] = str(window_start + self.window_size)
        
        return response


@asynccontextmanager
async def performance_context():
    """Context manager for performance monitoring."""
    start_time = time.time()
    start_memory = 0  # Could use psutil to get actual memory usage
    
    try:
        yield
    finally:
        end_time = time.time()
        duration = end_time - start_time
        
        if duration > 1.0:  # Log operations taking more than 1 second
            logger.info(f"Long-running operation completed in {duration:.3f}s")


class PerformanceOptimizer:
    """Performance optimization utilities."""
    
    @staticmethod
    async def optimize_response_size(data: Any, max_size: int = 1024 * 1024) -> Any:
        """Optimize response size by truncating large data."""
        import json
        
        if isinstance(data, dict):
            serialized = json.dumps(data)
            if len(serialized) > max_size:
                # Implement data truncation logic
                if "posts" in data and isinstance(data["posts"], list):
                    # Reduce number of posts
                    original_count = len(data["posts"])
                    data["posts"] = data["posts"][:min(50, original_count)]
                    data["truncated"] = True
                    data["original_count"] = original_count
                
                logger.warning(f"Response truncated due to size: {len(serialized)} bytes")
        
        return data
    
    @staticmethod
    async def batch_database_operations(operations: list, batch_size: int = 100):
        """Execute database operations in batches."""
        results = []
        
        for i in range(0, len(operations), batch_size):
            batch = operations[i:i + batch_size]
            batch_results = []
            
            for operation in batch:
                try:
                    if asyncio.iscoroutinefunction(operation):
                        result = await operation()
                    else:
                        result = operation()
                    batch_results.append(result)
                except Exception as e:
                    logger.error(f"Batch operation error: {e}")
                    batch_results.append(None)
            
            results.extend(batch_results)
            
            # Small delay between batches to prevent overwhelming the system
            if i + batch_size < len(operations):
                await asyncio.sleep(0.01)
        
        return results


# Global performance optimizer instance
performance_optimizer = PerformanceOptimizer()