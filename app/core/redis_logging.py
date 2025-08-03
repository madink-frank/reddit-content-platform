"""
Redis operation logging utilities.
"""

import time
import functools
import asyncio
from typing import Any, Callable, Dict, Optional, TypeVar, cast
import redis
from redis.asyncio import Redis as AsyncRedis

from app.core.logging import get_logger, ErrorCategory


logger = get_logger(__name__)

# Type variable for function return type
T = TypeVar('T')


def log_redis_operation(operation_type: str):
    """
    Decorator to log Redis operations with timing.
    
    Args:
        operation_type: Type of Redis operation (e.g., "get", "set", "delete")
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs) -> T:
            # Extract key if available
            key = None
            if len(args) > 1:
                key = args[1]  # Assuming first arg is self, second is key
            elif 'key' in kwargs:
                key = kwargs['key']
            
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                duration = (time.time() - start_time) * 1000  # Convert to ms
                
                # Log successful operation
                logger.debug(
                    f"Redis {operation_type}: {key}",
                    operation="redis_operation",
                    redis_operation=operation_type,
                    key=str(key)[:100] if key else "unknown",  # Truncate long keys
                    duration=duration,
                    cache_hit=result is not None if operation_type == "get" else None
                )
                
                return result
            except Exception as e:
                duration = (time.time() - start_time) * 1000
                
                # Log failed operation
                logger.error(
                    f"Redis {operation_type} failed: {key}",
                    error_category=ErrorCategory.REDIS,
                    alert_level="medium" if operation_type in ["set", "delete"] else "low",
                    operation="redis_operation_failed",
                    redis_operation=operation_type,
                    key=str(key)[:100] if key else "unknown",
                    duration=duration,
                    error=str(e),
                    exc_info=True
                )
                
                raise
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs) -> T:
            # Extract key if available
            key = None
            if len(args) > 1:
                key = args[1]  # Assuming first arg is self, second is key
            elif 'key' in kwargs:
                key = kwargs['key']
            
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                duration = (time.time() - start_time) * 1000  # Convert to ms
                
                # Log successful operation
                logger.debug(
                    f"Redis {operation_type}: {key}",
                    operation="redis_operation",
                    redis_operation=operation_type,
                    key=str(key)[:100] if key else "unknown",  # Truncate long keys
                    duration=duration,
                    cache_hit=result is not None if operation_type == "get" else None
                )
                
                return result
            except Exception as e:
                duration = (time.time() - start_time) * 1000
                
                # Log failed operation
                logger.error(
                    f"Redis {operation_type} failed: {key}",
                    error_category=ErrorCategory.REDIS,
                    alert_level="medium" if operation_type in ["set", "delete"] else "low",
                    operation="redis_operation_failed",
                    redis_operation=operation_type,
                    key=str(key)[:100] if key else "unknown",
                    duration=duration,
                    error=str(e),
                    exc_info=True
                )
                
                raise
        
        # Return appropriate wrapper based on whether the function is async
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper
    
    return decorator


class LoggedRedis:
    """
    Redis client wrapper with automatic logging.
    """
    
    def __init__(self, redis_client: redis.Redis):
        """
        Initialize the logged Redis client.
        
        Args:
            redis_client: Redis client to wrap
        """
        self.redis = redis_client
    
    @log_redis_operation("get")
    def get(self, key: str) -> Any:
        """Get value from Redis with logging."""
        return self.redis.get(key)
    
    @log_redis_operation("set")
    def set(self, key: str, value: Any, ex: Optional[int] = None) -> bool:
        """Set value in Redis with logging."""
        return self.redis.set(key, value, ex=ex)
    
    @log_redis_operation("delete")
    def delete(self, key: str) -> int:
        """Delete key from Redis with logging."""
        return self.redis.delete(key)
    
    @log_redis_operation("exists")
    def exists(self, key: str) -> bool:
        """Check if key exists in Redis with logging."""
        return bool(self.redis.exists(key))
    
    @log_redis_operation("expire")
    def expire(self, key: str, time: int) -> bool:
        """Set key expiration with logging."""
        return self.redis.expire(key, time)
    
    @log_redis_operation("ttl")
    def ttl(self, key: str) -> int:
        """Get key TTL with logging."""
        return self.redis.ttl(key)
    
    @log_redis_operation("incr")
    def incr(self, key: str) -> int:
        """Increment value with logging."""
        return self.redis.incr(key)
    
    @log_redis_operation("hget")
    def hget(self, name: str, key: str) -> Any:
        """Get hash field with logging."""
        return self.redis.hget(name, key)
    
    @log_redis_operation("hset")
    def hset(self, name: str, key: str, value: Any) -> int:
        """Set hash field with logging."""
        return self.redis.hset(name, key, value)
    
    @log_redis_operation("hdel")
    def hdel(self, name: str, *keys) -> int:
        """Delete hash fields with logging."""
        return self.redis.hdel(name, *keys)


class LoggedAsyncRedis:
    """
    Async Redis client wrapper with automatic logging.
    """
    
    def __init__(self, redis_client: AsyncRedis):
        """
        Initialize the logged async Redis client.
        
        Args:
            redis_client: Async Redis client to wrap
        """
        self.redis = redis_client
    
    @log_redis_operation("get")
    async def get(self, key: str) -> Any:
        """Get value from Redis with logging."""
        return await self.redis.get(key)
    
    @log_redis_operation("set")
    async def set(self, key: str, value: Any, ex: Optional[int] = None) -> bool:
        """Set value in Redis with logging."""
        return await self.redis.set(key, value, ex=ex)
    
    @log_redis_operation("delete")
    async def delete(self, key: str) -> int:
        """Delete key from Redis with logging."""
        return await self.redis.delete(key)
    
    @log_redis_operation("exists")
    async def exists(self, key: str) -> bool:
        """Check if key exists in Redis with logging."""
        return bool(await self.redis.exists(key))
    
    @log_redis_operation("expire")
    async def expire(self, key: str, time: int) -> bool:
        """Set key expiration with logging."""
        return await self.redis.expire(key, time)
    
    @log_redis_operation("ttl")
    async def ttl(self, key: str) -> int:
        """Get key TTL with logging."""
        return await self.redis.ttl(key)
    
    @log_redis_operation("incr")
    async def incr(self, key: str) -> int:
        """Increment value with logging."""
        return await self.redis.incr(key)
    
    @log_redis_operation("hget")
    async def hget(self, name: str, key: str) -> Any:
        """Get hash field with logging."""
        return await self.redis.hget(name, key)
    
    @log_redis_operation("hset")
    async def hset(self, name: str, key: str, value: Any) -> int:
        """Set hash field with logging."""
        return await self.redis.hset(name, key, value)
    
    @log_redis_operation("hdel")
    async def hdel(self, name: str, *keys) -> int:
        """Delete hash fields with logging."""
        return await self.redis.hdel(name, *keys)