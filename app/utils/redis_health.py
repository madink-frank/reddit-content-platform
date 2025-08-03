"""
Redis health check and connectivity utilities.
"""

import asyncio
import logging
from typing import Dict, Any
from app.core.redis_client import redis_client, cache_manager, session_manager
from app.core.config import settings

logger = logging.getLogger(__name__)


async def check_redis_connectivity() -> Dict[str, Any]:
    """
    Check Redis connectivity and return detailed status.
    
    Returns:
        Dict containing connection status, error details, and basic info
    """
    result = {
        "connected": False,
        "error": None,
        "redis_url": settings.REDIS_URL,
        "info": {}
    }
    
    try:
        # Test basic connectivity
        ping_result = await redis_client.ping()
        if ping_result:
            result["connected"] = True
            
            # Get cache info if connected
            cache_info = await cache_manager.get_cache_info()
            result["info"] = cache_info
            
            logger.info("Redis connectivity check: SUCCESS")
        else:
            result["error"] = "Redis ping returned False"
            logger.warning("Redis connectivity check: FAILED - ping returned False")
            
    except Exception as e:
        result["error"] = str(e)
        logger.error(f"Redis connectivity check: FAILED - {e}")
    
    return result


async def test_redis_operations() -> Dict[str, Any]:
    """
    Test basic Redis operations to ensure functionality.
    
    Returns:
        Dict containing test results for different operations
    """
    test_results = {
        "basic_operations": False,
        "json_operations": False,
        "expiration": False,
        "cache_manager": False,
        "session_manager": False,
        "errors": []
    }
    
    try:
        # Test basic operations
        test_key = "health_check_test"
        test_value = "test_value"
        
        if (await redis_client.set(test_key, test_value) and 
            await redis_client.get(test_key) == test_value and
            await redis_client.delete(test_key)):
            test_results["basic_operations"] = True
        
        # Test JSON operations
        json_key = "health_check_json"
        json_value = {"test": True, "timestamp": "2024-01-01"}
        
        if (await redis_client.set_json(json_key, json_value) and
            await redis_client.get_json(json_key) == json_value and
            await redis_client.delete(json_key)):
            test_results["json_operations"] = True
        
        # Test expiration
        expire_key = "health_check_expire"
        if (await redis_client.set(expire_key, "expire_test", 1) and
            await redis_client.ttl(expire_key) > 0):
            test_results["expiration"] = True
            await redis_client.delete(expire_key)
        
        # Test cache manager
        test_user_id = 99999
        test_user_data = {"id": test_user_id, "name": "Health Check User"}
        
        if (await cache_manager.cache_user(test_user_id, test_user_data, 60) and
            await cache_manager.get_cached_user(test_user_id) == test_user_data and
            await cache_manager.invalidate_user_cache(test_user_id)):
            test_results["cache_manager"] = True
        
        # Test session manager
        test_session_id = "health_check_session"
        test_session_user_id = 88888
        
        if (await session_manager.create_session(test_session_id, test_session_user_id, {}, 60) and
            await session_manager.get_session(test_session_id) is not None and
            await session_manager.delete_session(test_session_id)):
            test_results["session_manager"] = True
            
    except Exception as e:
        test_results["errors"].append(str(e))
        logger.error(f"Redis operations test failed: {e}")
    
    return test_results


async def get_redis_stats() -> Dict[str, Any]:
    """
    Get Redis statistics and performance metrics.
    
    Returns:
        Dict containing Redis statistics
    """
    stats = {
        "available": False,
        "cache_info": {},
        "key_counts": {},
        "errors": []
    }
    
    try:
        connectivity = await check_redis_connectivity()
        if connectivity["connected"]:
            stats["available"] = True
            stats["cache_info"] = connectivity["info"]
            
            # Count keys by prefix
            key_prefixes = [
                "user", "session", "keyword", "post", 
                "trend", "crawl", "content", "deploy", "metrics"
            ]
            
            for prefix in key_prefixes:
                pattern = f"{prefix}:*"
                keys = await redis_client.keys(pattern)
                stats["key_counts"][prefix] = len(keys)
                
        else:
            stats["errors"].append(connectivity["error"])
            
    except Exception as e:
        stats["errors"].append(str(e))
        logger.error(f"Failed to get Redis stats: {e}")
    
    return stats


async def cleanup_test_data():
    """Clean up any test data that might be left in Redis."""
    try:
        test_patterns = [
            "health_check_*",
            "test_*"
        ]
        
        cleaned_count = 0
        for pattern in test_patterns:
            keys = await redis_client.keys(pattern)
            for key in keys:
                if await redis_client.delete(key):
                    cleaned_count += 1
        
        logger.info(f"Cleaned up {cleaned_count} test keys from Redis")
        return cleaned_count
        
    except Exception as e:
        logger.error(f"Failed to cleanup test data: {e}")
        return 0


if __name__ == "__main__":
    async def main():
        print("🔍 Checking Redis connectivity...")
        connectivity = await check_redis_connectivity()
        print(f"Connected: {connectivity['connected']}")
        if connectivity['error']:
            print(f"Error: {connectivity['error']}")
        
        if connectivity['connected']:
            print("\n🧪 Testing Redis operations...")
            test_results = await test_redis_operations()
            for operation, success in test_results.items():
                if operation != "errors":
                    status = "✅" if success else "❌"
                    print(f"{status} {operation}: {success}")
            
            if test_results["errors"]:
                print(f"Errors: {test_results['errors']}")
            
            print("\n📊 Redis statistics...")
            stats = await get_redis_stats()
            if stats["available"]:
                print(f"Cache info: {stats['cache_info']}")
                print(f"Key counts: {stats['key_counts']}")
            
            print("\n🧹 Cleaning up test data...")
            cleaned = await cleanup_test_data()
            print(f"Cleaned {cleaned} test keys")
        
        # Close connections
        await redis_client.close()
    
    asyncio.run(main())