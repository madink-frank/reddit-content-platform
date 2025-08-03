"""
Test Redis cache and session management implementation.
"""

import pytest
import asyncio
from datetime import datetime
from app.core.redis_client import redis_client, cache_manager, session_manager, CacheKeyManager


@pytest.mark.asyncio
async def test_redis_connection():
    """Test Redis connection."""
    result = await redis_client.ping()
    assert result is True


@pytest.mark.asyncio
async def test_basic_cache_operations():
    """Test basic cache operations."""
    # Test string operations
    key = "test_key"
    value = "test_value"
    
    # Set and get
    assert await redis_client.set(key, value) is True
    assert await redis_client.get(key) == value
    
    # Check existence
    assert await redis_client.exists(key) is True
    
    # Delete
    assert await redis_client.delete(key) is True
    assert await redis_client.exists(key) is False


@pytest.mark.asyncio
async def test_json_cache_operations():
    """Test JSON cache operations."""
    key = "test_json_key"
    value = {"name": "test", "count": 42, "active": True}
    
    # Set and get JSON
    assert await redis_client.set_json(key, value) is True
    result = await redis_client.get_json(key)
    assert result == value
    
    # Clean up
    await redis_client.delete(key)


@pytest.mark.asyncio
async def test_cache_expiration():
    """Test cache expiration."""
    key = "test_expire_key"
    value = "test_value"
    expire_seconds = 2
    
    # Set with expiration
    assert await redis_client.set(key, value, expire_seconds) is True
    assert await redis_client.get(key) == value
    
    # Check TTL
    ttl = await redis_client.ttl(key)
    assert ttl > 0 and ttl <= expire_seconds
    
    # Wait for expiration
    await asyncio.sleep(expire_seconds + 1)
    assert await redis_client.get(key) is None


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
async def test_cache_manager_user_operations():
    """Test cache manager user operations."""
    user_id = 123
    user_data = {
        "id": user_id,
        "name": "Test User",
        "email": "test@example.com"
    }
    
    # Cache user
    assert await cache_manager.cache_user(user_id, user_data, 60) is True
    
    # Get cached user
    cached_user = await cache_manager.get_cached_user(user_id)
    assert cached_user == user_data
    
    # Invalidate cache
    assert await cache_manager.invalidate_user_cache(user_id) is True
    assert await cache_manager.get_cached_user(user_id) is None


@pytest.mark.asyncio
async def test_cache_manager_keywords_operations():
    """Test cache manager keywords operations."""
    user_id = 456
    keywords = [
        {"id": 1, "keyword": "python", "active": True},
        {"id": 2, "keyword": "fastapi", "active": True}
    ]
    
    # Cache keywords
    assert await cache_manager.cache_user_keywords(user_id, keywords, 60) is True
    
    # Get cached keywords
    cached_keywords = await cache_manager.get_cached_user_keywords(user_id)
    assert cached_keywords == keywords
    
    # Invalidate cache
    assert await cache_manager.invalidate_user_keywords_cache(user_id) is True
    assert await cache_manager.get_cached_user_keywords(user_id) is None


@pytest.mark.asyncio
async def test_cache_manager_trend_operations():
    """Test cache manager trend operations."""
    keyword_id = 789
    trend_data = {
        "keyword_id": keyword_id,
        "tfidf_scores": {"python": 0.8, "fastapi": 0.6},
        "engagement_score": 85.5,
        "trend_velocity": 12.3,
        "analyzed_at": datetime.utcnow().isoformat()
    }
    
    # Cache trend data
    assert await cache_manager.cache_trend_data(keyword_id, trend_data, 60) is True
    
    # Get cached trend data
    cached_trend = await cache_manager.get_cached_trend_data(keyword_id)
    assert cached_trend == trend_data
    
    # Clean up
    key = CacheKeyManager.trend_data_key(keyword_id)
    await redis_client.delete(key)


@pytest.mark.asyncio
async def test_session_manager_operations():
    """Test session manager operations."""
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
    assert updated_session["data"]["language"] == "en"  # Should still be there
    
    # Extend session
    assert await session_manager.extend_session(session_id, 120) is True
    
    # Delete session
    assert await session_manager.delete_session(session_id) is True
    assert await session_manager.get_session(session_id) is None


@pytest.mark.asyncio
async def test_session_manager_user_sessions():
    """Test getting all sessions for a user."""
    user_id = 888
    session_ids = ["session_1", "session_2", "session_3"]
    
    # Create multiple sessions for the same user
    for session_id in session_ids:
        await session_manager.create_session(session_id, user_id, {}, 60)
    
    # Get user sessions
    user_sessions = await session_manager.get_user_sessions(user_id)
    assert len(user_sessions) == 3
    
    session_ids_found = [s["session_id"] for s in user_sessions]
    for session_id in session_ids:
        assert session_id in session_ids_found
    
    # Clean up
    for session_id in session_ids:
        await session_manager.delete_session(session_id)


@pytest.mark.asyncio
async def test_cache_info():
    """Test cache information retrieval."""
    cache_info = await cache_manager.get_cache_info()
    assert isinstance(cache_info, dict)
    # Should have some basic Redis info keys
    expected_keys = ["connected_clients", "used_memory", "keyspace_hits", "keyspace_misses"]
    for key in expected_keys:
        assert key in cache_info


if __name__ == "__main__":
    # Run tests
    asyncio.run(test_redis_connection())
    asyncio.run(test_basic_cache_operations())
    asyncio.run(test_json_cache_operations())
    asyncio.run(test_cache_key_manager())
    asyncio.run(test_cache_manager_user_operations())
    asyncio.run(test_cache_manager_keywords_operations())
    asyncio.run(test_cache_manager_trend_operations())
    asyncio.run(test_session_manager_operations())
    asyncio.run(test_session_manager_user_sessions())
    asyncio.run(test_cache_info())
    print("All Redis tests passed!")