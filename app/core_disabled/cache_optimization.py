"""
Enhanced Redis caching strategies and optimization utilities.
"""

import asyncio
import json
import logging
import hashlib
from typing import Any, Dict, List, Optional, Union, Callable
from datetime import datetime, timedelta
from functools import wraps
from dataclasses import dataclass

from app.core.redis_client import redis_client, cache_manager
from app.core.config import settings

logger = logging.getLogger(__name__)


@dataclass
class CacheConfig:
    """Cache configuration for different data types."""
    ttl: int
    prefix: str
    compress: bool = False
    serialize_json: bool = True


class CacheStrategy:
    """Cache strategy definitions for different data types."""
    
    # Short-term cache (5 minutes)
    REALTIME = CacheConfig(ttl=300, prefix="rt", compress=False)
    
    # Medium-term cache (30 minutes)
    FREQUENT = CacheConfig(ttl=1800, prefix="freq", compress=True)
    
    # Long-term cache (2 hours)
    STABLE = CacheConfig(ttl=7200, prefix="stable", compress=True)
    
    # Very long-term cache (24 hours)
    STATIC = CacheConfig(ttl=86400, prefix="static", compress=True)


class SmartCacheManager:
    """Enhanced cache manager with intelligent caching strategies."""
    
    def __init__(self):
        self.redis = redis_client
        self.hit_count = 0
        self.miss_count = 0
        self.error_count = 0
    
    def _generate_cache_key(self, prefix: str, *args, **kwargs) -> str:
        """Generate consistent cache key from arguments."""
        # Create a hash of all arguments for consistent key generation
        key_data = f"{prefix}:{args}:{sorted(kwargs.items())}"
        key_hash = hashlib.md5(key_data.encode()).hexdigest()[:12]
        return f"{prefix}:{key_hash}"
    
    async def get_or_set(
        self,
        key: str,
        fetch_func: Callable,
        config: CacheConfig,
        *args,
        **kwargs
    ) -> Any:
        """
        Get from cache or execute function and cache result.
        """
        try:
            # Try to get from cache first
            cached_value = await self.redis.get_json(key)
            if cached_value is not None:
                self.hit_count += 1
                logger.debug(f"Cache hit for key: {key}")
                return cached_value
            
            # Cache miss - execute function
            self.miss_count += 1
            logger.debug(f"Cache miss for key: {key}")
            
            # Execute the function
            if asyncio.iscoroutinefunction(fetch_func):
                result = await fetch_func(*args, **kwargs)
            else:
                result = fetch_func(*args, **kwargs)
            
            # Cache the result
            await self.redis.set_json(key, result, config.ttl)
            
            return result
            
        except Exception as e:
            self.error_count += 1
            logger.error(f"Cache error for key {key}: {e}")
            # Fallback to direct function execution
            if asyncio.iscoroutinefunction(fetch_func):
                return await fetch_func(*args, **kwargs)
            else:
                return fetch_func(*args, **kwargs)
    
    async def invalidate_pattern(self, pattern: str) -> int:
        """Invalidate all keys matching pattern."""
        try:
            keys = await self.redis.keys(pattern)
            if not keys:
                return 0
            
            deleted_count = 0
            # Delete in batches to avoid blocking Redis
            batch_size = 100
            for i in range(0, len(keys), batch_size):
                batch = keys[i:i + batch_size]
                for key in batch:
                    if await self.redis.delete(key):
                        deleted_count += 1
                
                # Small delay between batches
                if i + batch_size < len(keys):
                    await asyncio.sleep(0.001)
            
            logger.info(f"Invalidated {deleted_count} keys matching pattern: {pattern}")
            return deleted_count
            
        except Exception as e:
            logger.error(f"Error invalidating pattern {pattern}: {e}")
            return 0
    
    async def warm_cache(self, warm_functions: List[Dict[str, Any]]):
        """Warm up cache with frequently accessed data."""
        logger.info("Starting cache warm-up process")
        
        for func_config in warm_functions:
            try:
                func = func_config["function"]
                key = func_config["key"]
                config = func_config["config"]
                args = func_config.get("args", [])
                kwargs = func_config.get("kwargs", {})
                
                # Check if already cached
                if not await self.redis.exists(key):
                    if asyncio.iscoroutinefunction(func):
                        result = await func(*args, **kwargs)
                    else:
                        result = func(*args, **kwargs)
                    
                    await self.redis.set_json(key, result, config.ttl)
                    logger.debug(f"Warmed cache for key: {key}")
                
            except Exception as e:
                logger.error(f"Error warming cache for {func_config.get('key', 'unknown')}: {e}")
        
        logger.info("Cache warm-up process completed")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache performance statistics."""
        total_requests = self.hit_count + self.miss_count
        hit_rate = (self.hit_count / total_requests * 100) if total_requests > 0 else 0
        
        return {
            "hit_count": self.hit_count,
            "miss_count": self.miss_count,
            "error_count": self.error_count,
            "hit_rate_percent": round(hit_rate, 2),
            "total_requests": total_requests
        }


class CacheDecorator:
    """Decorator for automatic caching of function results."""
    
    def __init__(self, config: CacheConfig, key_prefix: str = None):
        self.config = config
        self.key_prefix = key_prefix or config.prefix
        self.cache_manager = SmartCacheManager()
    
    def __call__(self, func: Callable):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            # Generate cache key
            key = self.cache_manager._generate_cache_key(
                self.key_prefix, func.__name__, *args, **kwargs
            )
            
            return await self.cache_manager.get_or_set(
                key, func, self.config, *args, **kwargs
            )
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            # For sync functions, we need to run in async context
            loop = asyncio.get_event_loop()
            return loop.run_until_complete(async_wrapper(*args, **kwargs))
        
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper


class LayeredCache:
    """Multi-layered caching system with different TTLs."""
    
    def __init__(self):
        self.redis = redis_client
        self.layers = {
            "l1": {"ttl": 300, "prefix": "l1"},      # 5 minutes
            "l2": {"ttl": 1800, "prefix": "l2"},     # 30 minutes
            "l3": {"ttl": 7200, "prefix": "l3"},     # 2 hours
        }
    
    async def get_layered(self, base_key: str, fetch_func: Callable, *args, **kwargs) -> Any:
        """Get data from layered cache system."""
        
        # Try each layer in order
        for layer_name, layer_config in self.layers.items():
            layer_key = f"{layer_config['prefix']}:{base_key}"
            
            try:
                cached_value = await self.redis.get_json(layer_key)
                if cached_value is not None:
                    logger.debug(f"Cache hit in layer {layer_name} for key: {base_key}")
                    
                    # Promote to higher layers
                    await self._promote_to_higher_layers(base_key, cached_value, layer_name)
                    return cached_value
                    
            except Exception as e:
                logger.error(f"Error accessing layer {layer_name} for key {base_key}: {e}")
                continue
        
        # Cache miss in all layers - fetch data
        logger.debug(f"Cache miss in all layers for key: {base_key}")
        
        if asyncio.iscoroutinefunction(fetch_func):
            result = await fetch_func(*args, **kwargs)
        else:
            result = fetch_func(*args, **kwargs)
        
        # Store in all layers
        await self._store_in_all_layers(base_key, result)
        
        return result
    
    async def _promote_to_higher_layers(self, base_key: str, value: Any, current_layer: str):
        """Promote cached value to higher (faster) layers."""
        layer_names = list(self.layers.keys())
        current_index = layer_names.index(current_layer)
        
        # Promote to all higher layers
        for i in range(current_index):
            layer_name = layer_names[i]
            layer_config = self.layers[layer_name]
            layer_key = f"{layer_config['prefix']}:{base_key}"
            
            try:
                await self.redis.set_json(layer_key, value, layer_config["ttl"])
            except Exception as e:
                logger.error(f"Error promoting to layer {layer_name}: {e}")
    
    async def _store_in_all_layers(self, base_key: str, value: Any):
        """Store value in all cache layers."""
        for layer_name, layer_config in self.layers.items():
            layer_key = f"{layer_config['prefix']}:{base_key}"
            
            try:
                await self.redis.set_json(layer_key, value, layer_config["ttl"])
            except Exception as e:
                logger.error(f"Error storing in layer {layer_name}: {e}")


class CacheWarmupService:
    """Service for cache warm-up operations."""
    
    def __init__(self):
        self.cache_manager = SmartCacheManager()
        self.layered_cache = LayeredCache()
    
    async def warmup_user_data(self, user_id: int):
        """Warm up cache for user-specific data."""
        from app.services.keyword_service import KeywordService
        from app.services.post_service import PostService
        from app.core.database import get_db_session
        
        try:
            with get_db_session() as db:
                keyword_service = KeywordService(db)
                post_service = PostService(db)
                
                # Warm up user keywords
                keywords, _ = await keyword_service.get_user_keywords(user_id, active_only=True)
                
                # Warm up recent posts for each keyword
                for keyword in keywords[:5]:  # Limit to top 5 keywords
                    await post_service.get_posts_by_keyword(
                        keyword.id, user_id, page=1, per_page=20
                    )
                
                logger.info(f"Cache warmed up for user {user_id}")
                
        except Exception as e:
            logger.error(f"Error warming up cache for user {user_id}: {e}")
    
    async def warmup_trending_data(self):
        """Warm up cache for trending data."""
        from app.services.trend_analysis_service import TrendAnalysisService
        from app.core.database import get_db_session
        
        try:
            with get_db_session() as db:
                trend_service = TrendAnalysisService()
                
                # Get active keywords from database
                from app.models.keyword import Keyword
                active_keywords = db.query(Keyword).filter(
                    Keyword.is_active == True
                ).limit(20).all()
                
                # Warm up trend data for active keywords
                for keyword in active_keywords:
                    await trend_service.analyze_keyword_trends(keyword.id, db)
                
                logger.info("Trending data cache warmed up")
                
        except Exception as e:
            logger.error(f"Error warming up trending data cache: {e}")


class CacheMetrics:
    """Cache performance metrics collection."""
    
    def __init__(self):
        self.metrics = {
            "hits": 0,
            "misses": 0,
            "errors": 0,
            "invalidations": 0,
            "warmups": 0
        }
        self.start_time = datetime.utcnow()
    
    def record_hit(self):
        self.metrics["hits"] += 1
    
    def record_miss(self):
        self.metrics["misses"] += 1
    
    def record_error(self):
        self.metrics["errors"] += 1
    
    def record_invalidation(self):
        self.metrics["invalidations"] += 1
    
    def record_warmup(self):
        self.metrics["warmups"] += 1
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get cache performance metrics."""
        total_requests = self.metrics["hits"] + self.metrics["misses"]
        hit_rate = (self.metrics["hits"] / total_requests * 100) if total_requests > 0 else 0
        
        uptime = (datetime.utcnow() - self.start_time).total_seconds()
        
        return {
            **self.metrics,
            "hit_rate_percent": round(hit_rate, 2),
            "total_requests": total_requests,
            "uptime_seconds": uptime,
            "requests_per_second": round(total_requests / uptime, 2) if uptime > 0 else 0
        }


# Global instances
smart_cache = SmartCacheManager()
layered_cache = LayeredCache()
cache_warmup = CacheWarmupService()
cache_metrics = CacheMetrics()

# Decorators for common caching patterns
cache_frequent = CacheDecorator(CacheStrategy.FREQUENT)
cache_stable = CacheDecorator(CacheStrategy.STABLE)
cache_static = CacheDecorator(CacheStrategy.STATIC)
cache_realtime = CacheDecorator(CacheStrategy.REALTIME)


# Cache warming functions for startup
async def initialize_cache_warmup():
    """Initialize cache with commonly accessed data."""
    logger.info("Starting cache initialization")
    
    try:
        # Warm up trending data
        await cache_warmup.warmup_trending_data()
        
        # Additional warmup tasks can be added here
        
        logger.info("Cache initialization completed")
        
    except Exception as e:
        logger.error(f"Error during cache initialization: {e}")


# Cache cleanup task
async def cleanup_expired_cache():
    """Clean up expired cache entries."""
    try:
        # Get cache info
        info = await cache_manager.get_cache_info()
        logger.info(f"Cache cleanup - Current memory usage: {info.get('used_memory', 'unknown')}")
        
        # Redis automatically handles TTL expiration, but we can monitor
        # and log statistics
        
    except Exception as e:
        logger.error(f"Error during cache cleanup: {e}")