#!/usr/bin/env python3
"""
Test script to verify performance optimizations are working correctly.
"""

import asyncio
import time
import sys
import os

# Add app to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.database import get_db_session
from app.core.redis_client import redis_client
from app.core.cache_optimization import smart_cache, CacheStrategy
from app.core.database_optimization import OptimizedPostService, QueryOptimizer
from app.services.post_service import PostService


async def test_redis_performance():
    """Test Redis caching performance."""
    print("Testing Redis performance...")
    
    # Test basic Redis operations
    start_time = time.time()
    
    # Set operation
    await redis_client.set_json("test_key", {"test": "data", "timestamp": time.time()}, 300)
    
    # Get operation
    result = await redis_client.get_json("test_key")
    
    # Delete operation
    await redis_client.delete("test_key")
    
    end_time = time.time()
    
    print(f"✓ Redis operations completed in {(end_time - start_time) * 1000:.2f}ms")
    print(f"  Retrieved data: {result is not None}")
    
    return True


async def test_smart_cache():
    """Test smart cache functionality."""
    print("Testing smart cache...")
    
    call_count = 0
    
    async def expensive_function(value):
        nonlocal call_count
        call_count += 1
        await asyncio.sleep(0.1)  # Simulate expensive operation
        return {"result": value, "call_count": call_count}
    
    # First call - should execute function
    start_time = time.time()
    result1 = await smart_cache.get_or_set(
        "test_cache_key",
        expensive_function,
        CacheStrategy.FREQUENT,
        "test_value"
    )
    first_call_time = time.time() - start_time
    
    # Second call - should use cache
    start_time = time.time()
    result2 = await smart_cache.get_or_set(
        "test_cache_key",
        expensive_function,
        CacheStrategy.FREQUENT,
        "test_value"
    )
    second_call_time = time.time() - start_time
    
    print(f"✓ First call (cache miss): {first_call_time * 1000:.2f}ms")
    print(f"✓ Second call (cache hit): {second_call_time * 1000:.2f}ms")
    print(f"  Cache speedup: {first_call_time / second_call_time:.1f}x faster")
    print(f"  Function called {call_count} times (should be 1)")
    
    # Clean up
    await redis_client.delete("test_cache_key")
    
    return second_call_time < first_call_time and call_count == 1


def test_database_indexes():
    """Test that database indexes are created."""
    print("Testing database indexes...")
    
    try:
        QueryOptimizer.create_performance_indexes()
        print("✓ Database indexes created successfully")
        return True
    except Exception as e:
        print(f"✗ Failed to create indexes: {e}")
        return False


def test_optimized_queries():
    """Test optimized database queries."""
    print("Testing optimized database queries...")
    
    try:
        with get_db_session() as db:
            # Test optimized post service
            optimized_service = OptimizedPostService(db)
            
            # Test statistics query
            start_time = time.time()
            stats = optimized_service.get_post_statistics_optimized(user_id=1)
            query_time = time.time() - start_time
            
            print(f"✓ Optimized statistics query completed in {query_time * 1000:.2f}ms")
            print(f"  Stats keys: {list(stats.keys())}")
            
            return True
            
    except Exception as e:
        print(f"✗ Optimized query test failed: {e}")
        return False


async def test_service_caching():
    """Test service-level caching."""
    print("Testing service-level caching...")
    
    try:
        with get_db_session() as db:
            service = PostService(db)
            
            # First call - should hit database
            start_time = time.time()
            stats1 = await service.get_post_statistics(user_id=1)
            first_call_time = time.time() - start_time
            
            # Second call - should use cache
            start_time = time.time()
            stats2 = await service.get_post_statistics(user_id=1)
            second_call_time = time.time() - start_time
            
            print(f"✓ First call (database): {first_call_time * 1000:.2f}ms")
            print(f"✓ Second call (cached): {second_call_time * 1000:.2f}ms")
            
            if second_call_time < first_call_time:
                print(f"  Cache speedup: {first_call_time / second_call_time:.1f}x faster")
                return True
            else:
                print("  Warning: Second call not faster (cache may not be working)")
                return False
                
    except Exception as e:
        print(f"✗ Service caching test failed: {e}")
        return False


async def test_cache_metrics():
    """Test cache metrics collection."""
    print("Testing cache metrics...")
    
    from app.core.cache_optimization import cache_metrics
    
    # Record some test metrics
    cache_metrics.record_hit()
    cache_metrics.record_hit()
    cache_metrics.record_miss()
    
    metrics = cache_metrics.get_metrics()
    
    print(f"✓ Cache metrics collected:")
    print(f"  Hits: {metrics['hits']}")
    print(f"  Misses: {metrics['misses']}")
    print(f"  Hit rate: {metrics['hit_rate_percent']}%")
    
    return metrics['hits'] == 2 and metrics['misses'] == 1


async def run_performance_tests():
    """Run all performance optimization tests."""
    print("=" * 60)
    print("PERFORMANCE OPTIMIZATION TESTS")
    print("=" * 60)
    
    tests = [
        ("Redis Performance", test_redis_performance()),
        ("Smart Cache", test_smart_cache()),
        ("Database Indexes", test_database_indexes()),
        ("Optimized Queries", test_optimized_queries()),
        ("Service Caching", test_service_caching()),
        ("Cache Metrics", test_cache_metrics()),
    ]
    
    results = []
    
    for test_name, test_coro in tests:
        print(f"\n{test_name}:")
        print("-" * 40)
        
        try:
            if asyncio.iscoroutine(test_coro):
                result = await test_coro
            else:
                result = test_coro
            
            results.append((test_name, result))
            
        except Exception as e:
            print(f"✗ Test failed with exception: {e}")
            results.append((test_name, False))
    
    # Print summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        symbol = "✓" if result else "✗"
        print(f"{symbol} {test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nResults: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All performance optimization tests passed!")
        return True
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
        return False


async def main():
    """Main test function."""
    try:
        success = await run_performance_tests()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\nTests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())