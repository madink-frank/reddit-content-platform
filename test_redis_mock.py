"""
Test Redis cache and session management implementation with mocking.
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime
from app.core.redis_client import RedisClient, CacheManager, SessionManager, CacheKeyManager


class MockAsyncRedis:
    """Mock async Redis client for testing."""
    
    def __init__(self):
        self.data = {}
        self.ttl_data = {}
    
    async def get(self, key):
        return self.data.get(key)
    
    async def set(self, key, value):
        self.data[key] = value
        return True
    
    async def setex(self, key, seconds, value):
        self.data[key] = value
        self.ttl_data[key] = seconds
        return True
    
    async def delete(self, key):
        if key in self.data:
            del self.data[key]
            if key in self.ttl_data:
                del self.ttl_data[key]
            return True
        return False
    
    async def exists(self, key):
        return key in self.data
    
    async def expire(self, key, seconds):
        if key in self.data:
            self.ttl_data[key] = seconds
            return True
        return False
    
    async def ttl(self, key):
        return self.ttl_data.get(key, -1)
    
    async def keys(self, pattern="*"):
        if pattern == "*":
            return list(self.data.keys())
        # Simple pattern matching for testing
        return [k for k in self.data.keys() if pattern.replace("*", "") in k]
    
    async def ping(self):
        return True
    
    async def flushdb(self):
        self.data.clear()
        self.ttl_data.clear()
        return True
    
    async def info(self):
        return {
            "connected_clients": 1,
            "used_memory_human": "1MB",
            "keyspace_hits": 100,
            "keyspace_misses": 10,
            "total_commands_processed": 1000
        }
    
    async def close(self):
        pass


@pytest.fixture
def mock_redis_client():
    """Create a mock Redis client for testing."""
    client = RedisClient()
    mock_async_redis = MockAsyncRedis()
    
    async def get_mock_client():
        return mock_async_redis
    
    client.get_async_client = get_mock_client
    return client, mock_async_redis


@pytest.mark.asyncio
async def test_cache_key_manager():
    """Test cache key naming conventions."""
    keys = CacheKeyManager()
    
    # Test key generation
    assert keys.user_key(123) == "user:123"
    assert keys.session_key("abc123") == "session:abc123"
    assert keys.user_keywords_key(456) == "keyword:user:456"
    assert keys.keyword_posts_key(789) == "post:keyword:789"
    assert keys.trend_data_key(101) == "trend:keyword:101"
    assert keys.crawl_status_key("task123") == "crawl:status:task123"
    assert keys.content_key(202) == "content:202"
    assert keys.deployment_status_key("deploy123") == "deploy:status:deploy123"
    assert keys.metrics_key("api", "2024-01-01") == "metrics:api:2024-01-01"


@pytest.mark.asyncio
async def test_redis_basic_operations(mock_redis_client):
    """Test basic Redis operations with mock."""
    redis_client, mock_redis = mock_redis_client
    
    # Test ping
    assert await redis_client.ping() is True
    
    # Test string operations
    key = "test_key"
    value = "test_value"
    
    assert await redis_client.set(key, value) is True
    assert await redis_client.get(key) == value
    assert await redis_client.exists(key) is True
    assert await redis_client.delete(key) is True
    assert await redis_client.exists(key) is False


@pytest.mark.asyncio
async def test_redis_json_operations(mock_redis_client):
    """Test JSON operations with mock."""
    redis_client, mock_redis = mock_redis_client
    
    key = "test_json_key"
    value = {"name": "test", "count": 42, "active": True}
    
    assert await redis_client.set_json(key, value) is True
    result = await redis_client.get_json(key)
    assert result == value
    
    await redis_client.delete(key)


@pytest.mark.asyncio
async def test_cache_manager_operations(mock_redis_client):
    """Test cache manager operations with mock."""
    redis_client, mock_redis = mock_redis_client
    cache_manager = CacheManager(redis_client)
    
    # Test user caching
    user_id = 123
    user_data = {
        "id": user_id,
        "name": "Test User",
        "email": "test@example.com"
    }
    
    assert await cache_manager.cache_user(user_id, user_data, 60) is True
    cached_user = await cache_manager.get_cached_user(user_id)
    assert cached_user == user_data
    
    # Test keywords caching
    keywords = [
        {"id": 1, "keyword": "python", "active": True},
        {"id": 2, "keyword": "fastapi", "active": True}
    ]
    
    assert await cache_manager.cache_user_keywords(user_id, keywords, 60) is True
    cached_keywords = await cache_manager.get_cached_user_keywords(user_id)
    assert cached_keywords == keywords
    
    # Test trend data caching
    keyword_id = 789
    trend_data = {
        "keyword_id": keyword_id,
        "tfidf_scores": {"python": 0.8, "fastapi": 0.6},
        "engagement_score": 85.5,
        "trend_velocity": 12.3
    }
    
    assert await cache_manager.cache_trend_data(keyword_id, trend_data, 60) is True
    cached_trend = await cache_manager.get_cached_trend_data(keyword_id)
    assert cached_trend == trend_data


@pytest.mark.asyncio
async def test_session_manager_operations(mock_redis_client):
    """Test session manager operations with mock."""
    redis_client, mock_redis = mock_redis_client
    session_manager = SessionManager(redis_client)
    
    session_id = "test_session_123"
    user_id = 999
    session_data = {"theme": "dark", "language": "en"}
    
    # Create session
    assert await session_manager.create_session(session_id, user_id, session_data, 60) is True
    
    # Get session
    session = await session_manager.get_session(session_id)
    assert session is not None
    assert session["user_id"] == user_id
    assert session["data"] == session_data
    assert "created_at" in session
    assert "last_accessed" in session
    
    # Update session
    new_data = {"theme": "light"}
    assert await session_manager.update_session(session_id, new_data) is True
    
    updated_session = await session_manager.get_session(session_id)
    assert updated_session["data"]["theme"] == "light"
    assert updated_session["data"]["language"] == "en"
    
    # Delete session
    assert await session_manager.delete_session(session_id) is True
    assert await session_manager.get_session(session_id) is None


@pytest.mark.asyncio
async def test_cache_info(mock_redis_client):
    """Test cache information retrieval."""
    redis_client, mock_redis = mock_redis_client
    cache_manager = CacheManager(redis_client)
    
    cache_info = await cache_manager.get_cache_info()
    assert isinstance(cache_info, dict)
    expected_keys = ["connected_clients", "used_memory", "keyspace_hits", "keyspace_misses"]
    for key in expected_keys:
        assert key in cache_info


if __name__ == "__main__":
    # Run tests
    asyncio.run(test_cache_key_manager())
    print("✓ Cache key manager tests passed")
    
    # Create mock client for standalone testing
    client = RedisClient()
    mock_redis = MockAsyncRedis()
    
    async def get_mock_client():
        return mock_redis
    
    client.get_async_client = get_mock_client
    mock_client_tuple = (client, mock_redis)
    
    asyncio.run(test_redis_basic_operations(mock_client_tuple))
    print("✓ Basic Redis operations tests passed")
    
    asyncio.run(test_redis_json_operations(mock_client_tuple))
    print("✓ JSON operations tests passed")
    
    asyncio.run(test_cache_manager_operations(mock_client_tuple))
    print("✓ Cache manager tests passed")
    
    asyncio.run(test_session_manager_operations(mock_client_tuple))
    print("✓ Session manager tests passed")
    
    asyncio.run(test_cache_info(mock_client_tuple))
    print("✓ Cache info tests passed")
    
    print("\n🎉 All Redis implementation tests passed!")