"""
Redis client configuration and utilities for caching and session management.
"""

import redis
import redis.asyncio as aioredis
import json
import logging
from typing import Any, Optional, Union, Dict, List
from datetime import datetime, timedelta
from app.core.config import settings

logger = logging.getLogger(__name__)


class RedisConnectionPool:
    """Redis connection pool manager."""
    
    def __init__(self):
        self._pool = None
        self._async_pool = None
    
    def get_sync_pool(self) -> redis.ConnectionPool:
        """Get synchronous Redis connection pool."""
        if self._pool is None:
            self._pool = redis.ConnectionPool.from_url(
                settings.REDIS_URL,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5,
                retry_on_timeout=True,
                health_check_interval=30,
                max_connections=20
            )
        return self._pool
    
    def get_async_pool(self) -> aioredis.ConnectionPool:
        """Get asynchronous Redis connection pool."""
        if self._async_pool is None:
            self._async_pool = aioredis.ConnectionPool.from_url(
                settings.REDIS_URL,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5,
                retry_on_timeout=True,
                health_check_interval=30,
                max_connections=20
            )
        return self._async_pool


class RedisClient:
    """Redis client wrapper with utility methods."""
    
    def __init__(self):
        self.pool = RedisConnectionPool()
        self.redis = redis.Redis(connection_pool=self.pool.get_sync_pool())
        self._async_redis = None
    
    async def get_async_client(self) -> aioredis.Redis:
        """Get async Redis client."""
        if self._async_redis is None:
            self._async_redis = aioredis.Redis(connection_pool=self.pool.get_async_pool())
        return self._async_redis
    
    async def get(self, key: str) -> Optional[str]:
        """Get value by key."""
        try:
            client = await self.get_async_client()
            return await client.get(key)
        except redis.RedisError as e:
            logger.error(f"Redis GET error for key {key}: {e}")
            return None
    
    async def set(
        self, 
        key: str, 
        value: Union[str, dict, list], 
        expire: Optional[int] = None
    ) -> bool:
        """Set key-value pair with optional expiration."""
        try:
            client = await self.get_async_client()
            if isinstance(value, (dict, list)):
                value = json.dumps(value)
            
            if expire:
                return await client.setex(key, expire, value)
            else:
                return await client.set(key, value)
        except (redis.RedisError, json.JSONEncodeError) as e:
            logger.error(f"Redis SET error for key {key}: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete key."""
        try:
            client = await self.get_async_client()
            return bool(await client.delete(key))
        except redis.RedisError as e:
            logger.error(f"Redis DELETE error for key {key}: {e}")
            return False
    
    async def exists(self, key: str) -> bool:
        """Check if key exists."""
        try:
            client = await self.get_async_client()
            return bool(await client.exists(key))
        except redis.RedisError as e:
            logger.error(f"Redis EXISTS error for key {key}: {e}")
            return False
    
    async def expire(self, key: str, seconds: int) -> bool:
        """Set expiration time for key."""
        try:
            client = await self.get_async_client()
            return bool(await client.expire(key, seconds))
        except redis.RedisError as e:
            logger.error(f"Redis EXPIRE error for key {key}: {e}")
            return False
    
    async def ttl(self, key: str) -> int:
        """Get time to live for key."""
        try:
            client = await self.get_async_client()
            return await client.ttl(key)
        except redis.RedisError as e:
            logger.error(f"Redis TTL error for key {key}: {e}")
            return -1
    
    async def get_json(self, key: str) -> Optional[Union[dict, list]]:
        """Get JSON value by key."""
        try:
            client = await self.get_async_client()
            value = await client.get(key)
            if value:
                return json.loads(value)
            return None
        except (redis.RedisError, json.JSONDecodeError) as e:
            logger.error(f"Redis GET_JSON error for key {key}: {e}")
            return None
    
    async def set_json(
        self, 
        key: str, 
        value: Union[dict, list], 
        expire: Optional[int] = None
    ) -> bool:
        """Set JSON value with optional expiration."""
        try:
            client = await self.get_async_client()
            json_value = json.dumps(value, default=str)
            if expire:
                return await client.setex(key, expire, json_value)
            else:
                return await client.set(key, json_value)
        except (redis.RedisError, json.JSONEncodeError) as e:
            logger.error(f"Redis SET_JSON error for key {key}: {e}")
            return False
    
    async def ping(self) -> bool:
        """Check Redis connection."""
        try:
            client = await self.get_async_client()
            return await client.ping()
        except redis.RedisError as e:
            logger.error(f"Redis PING error: {e}")
            return False
    
    async def flushdb(self) -> bool:
        """Flush current database (use with caution)."""
        try:
            client = await self.get_async_client()
            return await client.flushdb()
        except redis.RedisError as e:
            logger.error(f"Redis FLUSHDB error: {e}")
            return False
    
    async def keys(self, pattern: str = "*") -> List[str]:
        """Get keys matching pattern."""
        try:
            client = await self.get_async_client()
            return await client.keys(pattern)
        except redis.RedisError as e:
            logger.error(f"Redis KEYS error for pattern {pattern}: {e}")
            return []
    
    async def close(self):
        """Close Redis connections."""
        try:
            if self._async_redis:
                await self._async_redis.close()
        except Exception as e:
            logger.error(f"Error closing Redis connection: {e}")


class CacheKeyManager:
    """Cache key naming convention manager."""
    
    # Key prefixes for different data types
    USER_PREFIX = "user"
    SESSION_PREFIX = "session"
    KEYWORD_PREFIX = "keyword"
    POST_PREFIX = "post"
    TREND_PREFIX = "trend"
    CRAWL_PREFIX = "crawl"
    CONTENT_PREFIX = "content"
    DEPLOYMENT_PREFIX = "deploy"
    METRICS_PREFIX = "metrics"
    
    @staticmethod
    def user_key(user_id: int) -> str:
        """Generate user cache key."""
        return f"{CacheKeyManager.USER_PREFIX}:{user_id}"
    
    @staticmethod
    def session_key(session_id: str) -> str:
        """Generate session cache key."""
        return f"{CacheKeyManager.SESSION_PREFIX}:{session_id}"
    
    @staticmethod
    def user_keywords_key(user_id: int) -> str:
        """Generate user keywords cache key."""
        return f"{CacheKeyManager.KEYWORD_PREFIX}:user:{user_id}"
    
    @staticmethod
    def keyword_posts_key(keyword_id: int) -> str:
        """Generate keyword posts cache key."""
        return f"{CacheKeyManager.POST_PREFIX}:keyword:{keyword_id}"
    
    @staticmethod
    def trend_data_key(keyword_id: int) -> str:
        """Generate trend data cache key."""
        return f"{CacheKeyManager.TREND_PREFIX}:keyword:{keyword_id}"
    
    @staticmethod
    def crawl_status_key(task_id: str) -> str:
        """Generate crawl status cache key."""
        return f"{CacheKeyManager.CRAWL_PREFIX}:status:{task_id}"
    
    @staticmethod
    def content_key(content_id: int) -> str:
        """Generate content cache key."""
        return f"{CacheKeyManager.CONTENT_PREFIX}:{content_id}"
    
    @staticmethod
    def deployment_status_key(deployment_id: str) -> str:
        """Generate deployment status cache key."""
        return f"{CacheKeyManager.DEPLOYMENT_PREFIX}:status:{deployment_id}"
    
    @staticmethod
    def metrics_key(metric_type: str, date: str) -> str:
        """Generate metrics cache key."""
        return f"{CacheKeyManager.METRICS_PREFIX}:{metric_type}:{date}"


class CacheManager:
    """High-level cache management with business logic."""
    
    def __init__(self, redis_client: RedisClient):
        self.redis = redis_client
        self.keys = CacheKeyManager()
    
    # User caching
    async def cache_user(self, user_id: int, user_data: dict, expire: int = 3600) -> bool:
        """Cache user data."""
        key = self.keys.user_key(user_id)
        return await self.redis.set_json(key, user_data, expire)
    
    async def get_cached_user(self, user_id: int) -> Optional[dict]:
        """Get cached user data."""
        key = self.keys.user_key(user_id)
        return await self.redis.get_json(key)
    
    async def invalidate_user_cache(self, user_id: int) -> bool:
        """Invalidate user cache."""
        key = self.keys.user_key(user_id)
        return await self.redis.delete(key)
    
    # Keywords caching
    async def cache_user_keywords(self, user_id: int, keywords: list, expire: int = 1800) -> bool:
        """Cache user keywords."""
        key = self.keys.user_keywords_key(user_id)
        return await self.redis.set_json(key, keywords, expire)
    
    async def get_cached_user_keywords(self, user_id: int) -> Optional[list]:
        """Get cached user keywords."""
        key = self.keys.user_keywords_key(user_id)
        return await self.redis.get_json(key)
    
    async def invalidate_user_keywords_cache(self, user_id: int) -> bool:
        """Invalidate user keywords cache."""
        key = self.keys.user_keywords_key(user_id)
        return await self.redis.delete(key)
    
    # Posts caching
    async def cache_keyword_posts(self, keyword_id: int, posts: list, expire: int = 900) -> bool:
        """Cache keyword posts."""
        key = self.keys.keyword_posts_key(keyword_id)
        return await self.redis.set_json(key, posts, expire)
    
    async def get_cached_keyword_posts(self, keyword_id: int) -> Optional[list]:
        """Get cached keyword posts."""
        key = self.keys.keyword_posts_key(keyword_id)
        return await self.redis.get_json(key)
    
    # Trend data caching
    async def cache_trend_data(self, keyword_id: int, trend_data: dict, expire: int = 1800) -> bool:
        """Cache trend analysis data."""
        key = self.keys.trend_data_key(keyword_id)
        return await self.redis.set_json(key, trend_data, expire)
    
    async def get_cached_trend_data(self, keyword_id: int) -> Optional[dict]:
        """Get cached trend data."""
        key = self.keys.trend_data_key(keyword_id)
        return await self.redis.get_json(key)
    
    # Task status caching
    async def cache_crawl_status(self, task_id: str, status_data: dict, expire: int = 3600) -> bool:
        """Cache crawling task status."""
        key = self.keys.crawl_status_key(task_id)
        return await self.redis.set_json(key, status_data, expire)
    
    async def get_crawl_status(self, task_id: str) -> Optional[dict]:
        """Get crawling task status."""
        key = self.keys.crawl_status_key(task_id)
        return await self.redis.get_json(key)
    
    # Content caching
    async def cache_content(self, content_id: int, content_data: dict, expire: int = 7200) -> bool:
        """Cache generated content."""
        key = self.keys.content_key(content_id)
        return await self.redis.set_json(key, content_data, expire)
    
    async def get_cached_content(self, content_id: int) -> Optional[dict]:
        """Get cached content."""
        key = self.keys.content_key(content_id)
        return await self.redis.get_json(key)
    
    # Deployment status caching
    async def cache_deployment_status(self, deployment_id: str, status_data: dict, expire: int = 1800) -> bool:
        """Cache deployment status."""
        key = self.keys.deployment_status_key(deployment_id)
        return await self.redis.set_json(key, status_data, expire)
    
    async def get_deployment_status(self, deployment_id: str) -> Optional[dict]:
        """Get deployment status."""
        key = self.keys.deployment_status_key(deployment_id)
        return await self.redis.get_json(key)
    
    # Metrics caching
    async def cache_metrics(self, metric_type: str, date: str, metrics_data: dict, expire: int = 3600) -> bool:
        """Cache metrics data."""
        key = self.keys.metrics_key(metric_type, date)
        return await self.redis.set_json(key, metrics_data, expire)
    
    async def get_cached_metrics(self, metric_type: str, date: str) -> Optional[dict]:
        """Get cached metrics."""
        key = self.keys.metrics_key(metric_type, date)
        return await self.redis.get_json(key)
    
    # Bulk operations
    async def invalidate_pattern(self, pattern: str) -> int:
        """Invalidate all keys matching pattern."""
        keys = await self.redis.keys(pattern)
        if not keys:
            return 0
        
        deleted_count = 0
        for key in keys:
            if await self.redis.delete(key):
                deleted_count += 1
        return deleted_count
    
    async def get_cache_info(self) -> dict:
        """Get cache information and statistics."""
        try:
            client = await self.redis.get_async_client()
            info = await client.info()
            return {
                "connected_clients": info.get("connected_clients", 0),
                "used_memory": info.get("used_memory_human", "0B"),
                "keyspace_hits": info.get("keyspace_hits", 0),
                "keyspace_misses": info.get("keyspace_misses", 0),
                "total_commands_processed": info.get("total_commands_processed", 0)
            }
        except Exception as e:
            logger.error(f"Error getting cache info: {e}")
            return {}


class SessionManager:
    """Session management utilities."""
    
    def __init__(self, redis_client: RedisClient):
        self.redis = redis_client
        self.keys = CacheKeyManager()
        self.default_expire = 3600  # 1 hour
    
    async def create_session(self, session_id: str, user_id: int, session_data: dict = None, expire: int = None) -> bool:
        """Create a new session."""
        if expire is None:
            expire = self.default_expire
        
        session_info = {
            "user_id": user_id,
            "created_at": datetime.utcnow().isoformat(),
            "last_accessed": datetime.utcnow().isoformat(),
            "data": session_data or {}
        }
        
        key = self.keys.session_key(session_id)
        return await self.redis.set_json(key, session_info, expire)
    
    async def get_session(self, session_id: str) -> Optional[dict]:
        """Get session data."""
        key = self.keys.session_key(session_id)
        session_data = await self.redis.get_json(key)
        
        if session_data:
            # Update last accessed time
            session_data["last_accessed"] = datetime.utcnow().isoformat()
            await self.redis.set_json(key, session_data, await self.redis.ttl(key))
        
        return session_data
    
    async def update_session(self, session_id: str, session_data: dict) -> bool:
        """Update session data."""
        key = self.keys.session_key(session_id)
        current_session = await self.redis.get_json(key)
        
        if not current_session:
            return False
        
        current_session["data"].update(session_data)
        current_session["last_accessed"] = datetime.utcnow().isoformat()
        
        ttl = await self.redis.ttl(key)
        return await self.redis.set_json(key, current_session, ttl if ttl > 0 else self.default_expire)
    
    async def delete_session(self, session_id: str) -> bool:
        """Delete session."""
        key = self.keys.session_key(session_id)
        return await self.redis.delete(key)
    
    async def extend_session(self, session_id: str, expire: int = None) -> bool:
        """Extend session expiration."""
        if expire is None:
            expire = self.default_expire
        
        key = self.keys.session_key(session_id)
        return await self.redis.expire(key, expire)
    
    async def get_user_sessions(self, user_id: int) -> List[dict]:
        """Get all sessions for a user."""
        pattern = f"{self.keys.SESSION_PREFIX}:*"
        keys = await self.redis.keys(pattern)
        
        user_sessions = []
        for key in keys:
            session_data = await self.redis.get_json(key)
            if session_data and session_data.get("user_id") == user_id:
                session_id = key.split(":")[-1]
                user_sessions.append({
                    "session_id": session_id,
                    "created_at": session_data.get("created_at"),
                    "last_accessed": session_data.get("last_accessed"),
                    "ttl": await self.redis.ttl(key)
                })
        
        return user_sessions
    
    async def cleanup_expired_sessions(self) -> int:
        """Clean up expired sessions (Redis handles this automatically, but useful for monitoring)."""
        pattern = f"{self.keys.SESSION_PREFIX}:*"
        keys = await self.redis.keys(pattern)
        
        expired_count = 0
        for key in keys:
            ttl = await self.redis.ttl(key)
            if ttl == -2:  # Key doesn't exist (expired)
                expired_count += 1
        
        return expired_count


# Global instances
redis_client = RedisClient()
cache_manager = CacheManager(redis_client)
session_manager = SessionManager(redis_client)