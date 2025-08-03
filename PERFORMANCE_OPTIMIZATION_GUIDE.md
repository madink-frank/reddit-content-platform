# Performance Optimization Guide

This guide covers the performance optimizations implemented in the Reddit Content Platform and how to use the load testing tools.

## Overview

The performance optimization implementation includes:

1. **Database Query Optimization** - Improved queries with indexes and optimized joins
2. **Enhanced Redis Caching** - Multi-layered caching with intelligent strategies
3. **API Response Time Optimization** - Middleware for performance monitoring and caching
4. **Load Testing with Locust** - Comprehensive load testing scenarios

## Database Optimizations

### Performance Indexes

The system automatically creates performance indexes on startup:

```sql
-- Posts by keyword and creation date (most common query)
CREATE INDEX idx_posts_keyword_created ON posts(keyword_id, created_at DESC);

-- Posts by score for trending queries
CREATE INDEX idx_posts_score ON posts(score DESC);

-- Composite index for search queries
CREATE INDEX idx_posts_search ON posts(keyword_id, post_created_at DESC, score DESC);

-- Comments by post_id
CREATE INDEX idx_comments_post_id ON comments(post_id);

-- Metrics by post_id and calculation time
CREATE INDEX idx_metrics_post_calculated ON metrics(post_id, calculated_at DESC);
```

### Optimized Queries

The `OptimizedPostService` provides enhanced query methods:

```python
from app.core.database_optimization import OptimizedPostService

# Get posts with metrics in a single optimized query
posts_data = service.get_posts_with_metrics_optimized(
    user_id=1, 
    keyword_id=None, 
    limit=50, 
    offset=0
)

# Get trending posts using window functions
trending = service.get_trending_posts_optimized(
    user_id=1, 
    hours=24, 
    limit=20
)

# Get comprehensive statistics in one query
stats = service.get_post_statistics_optimized(user_id=1)
```

### Query Performance Monitoring

The system automatically monitors slow queries:

```python
from app.core.database_optimization import query_monitor

# Get performance report
report = query_monitor.get_performance_report()
print(f"Slow queries: {len(report['slow_queries'])}")
```

## Redis Caching Optimizations

### Multi-layered Caching

The system implements a 3-layer cache strategy:

- **L1 Cache**: 5 minutes TTL for real-time data
- **L2 Cache**: 30 minutes TTL for frequently accessed data  
- **L3 Cache**: 2 hours TTL for stable data

```python
from app.core.cache_optimization import layered_cache

# Use layered caching
result = await layered_cache.get_layered(
    "user_posts:123", 
    fetch_posts_function, 
    user_id=123
)
```

### Smart Cache Manager

Intelligent caching with automatic fallback:

```python
from app.core.cache_optimization import smart_cache, CacheStrategy

# Use smart caching with automatic key generation
@cache_frequent  # 30-minute cache
async def get_user_data(user_id: int):
    return await fetch_user_data(user_id)

# Manual smart caching
result = await smart_cache.get_or_set(
    "custom_key",
    expensive_function,
    CacheStrategy.STABLE,  # 2-hour cache
    arg1, arg2, kwarg1="value"
)
```

### Cache Warming

The system automatically warms up cache on startup:

```python
from app.core.cache_optimization import cache_warmup

# Warm up user-specific data
await cache_warmup.warmup_user_data(user_id=1)

# Warm up trending data
await cache_warmup.warmup_trending_data()
```

## API Performance Middleware

### Performance Monitoring

Tracks request performance and identifies slow endpoints:

```python
# Automatic performance tracking
# Slow requests (>1s) are logged automatically
# Response headers include timing information:
# X-Process-Time: 0.123
# X-Request-ID: 1234567890-abc123
```

### Response Caching

Automatically caches GET responses for specific endpoints:

```python
# Cached endpoints (5-minute TTL):
# - /api/v1/posts
# - /api/v1/trends  
# - /api/v1/keywords
# - /api/v1/public-blog

# Cache headers indicate hit/miss:
# X-Cache: HIT or X-Cache: MISS
```

### Rate Limiting

Protects against abuse with configurable limits:

```python
# Default: 60 requests per minute per IP
# Headers show current status:
# X-RateLimit-Limit: 60
# X-RateLimit-Remaining: 45
# X-RateLimit-Reset: 1640995200
```

## Load Testing

### Running Load Tests with Locust

1. **Install Locust** (already in requirements.txt):
```bash
pip install locust
```

2. **Basic Load Test**:
```bash
# Start Locust web interface
locust -f locustfile.py --host=http://localhost:8000

# Open http://localhost:8089 in browser
# Configure users and spawn rate
# Start test and monitor results
```

3. **Command Line Load Test**:
```bash
# Run headless load test
locust -f locustfile.py --host=http://localhost:8000 \
  --users 50 --spawn-rate 5 --run-time 5m --headless
```

4. **Different User Types**:
```bash
# Test with specific user class
locust -f locustfile.py --host=http://localhost:8000 \
  RedditPlatformUser --users 20 --spawn-rate 2

# Test admin operations
locust -f locustfile.py --host=http://localhost:8000 \
  AdminUser --users 5 --spawn-rate 1
```

### Load Test Scenarios

The `locustfile.py` includes several user types:

1. **RedditPlatformUser** - Regular API usage patterns
2. **AdminUser** - Admin-specific operations (lower frequency)
3. **HighVolumeUser** - Stress testing with rapid requests

### Custom Load Shapes

Use predefined load patterns:

```bash
# Step load testing (gradual increase)
locust -f locustfile.py --host=http://localhost:8000 StepLoadShape

# Spike testing (sudden load increases)
locust -f locustfile.py --host=http://localhost:8000 SpikeLoadShape
```

### Performance Testing Script

Run comprehensive performance tests:

```bash
# Basic performance test
python scripts/performance_test.py

# Custom configuration
python scripts/performance_test.py \
  --base-url http://localhost:8000 \
  --api-requests 100 \
  --db-queries 50 \
  --redis-ops 1000 \
  --threads 10 \
  --output performance_results.json
```

The script tests:
- API endpoint response times
- Database query performance
- Redis operation speed
- Concurrent load handling
- System resource usage

## Performance Monitoring

### Real-time Metrics

Monitor performance through various endpoints:

```bash
# Basic health check
curl http://localhost:8000/health

# Detailed health with component status
curl http://localhost:8000/health/detailed

# Specific service health
curl http://localhost:8000/health/database
curl http://localhost:8000/health/redis

# Prometheus metrics
curl http://localhost:8000/metrics
```

### Performance Reports

Get detailed performance reports:

```python
from app.core.database_optimization import query_monitor
from app.core.cache_optimization import cache_metrics

# Database performance
db_report = query_monitor.get_performance_report()

# Cache performance  
cache_stats = cache_metrics.get_metrics()
print(f"Cache hit rate: {cache_stats['hit_rate_percent']}%")
```

## Best Practices

### Database Optimization

1. **Use Optimized Services**: Prefer `OptimizedPostService` over basic queries
2. **Batch Operations**: Use batch methods for multiple operations
3. **Index Usage**: Ensure queries use appropriate indexes
4. **Connection Pooling**: Monitor connection pool usage

### Caching Strategy

1. **Cache Frequently Accessed Data**: Use appropriate TTL values
2. **Cache Invalidation**: Invalidate cache when data changes
3. **Layered Caching**: Use multi-layer cache for different access patterns
4. **Cache Warming**: Warm up cache for critical data

### API Performance

1. **Pagination**: Always use pagination for large datasets
2. **Filtering**: Apply filters at the database level
3. **Compression**: Enable response compression for large payloads
4. **Monitoring**: Monitor slow requests and optimize accordingly

### Load Testing

1. **Realistic Scenarios**: Test with realistic user behavior patterns
2. **Gradual Load Increase**: Start with low load and gradually increase
3. **Monitor Resources**: Watch CPU, memory, and database performance
4. **Test Different Endpoints**: Include all critical API endpoints

## Troubleshooting

### Common Performance Issues

1. **Slow Database Queries**:
   - Check query execution plans
   - Ensure proper indexes exist
   - Consider query optimization

2. **High Cache Miss Rate**:
   - Review cache TTL settings
   - Check cache key generation
   - Monitor cache invalidation patterns

3. **High API Response Times**:
   - Check middleware performance
   - Review database connection pooling
   - Monitor external API calls

4. **Memory Usage Issues**:
   - Monitor Redis memory usage
   - Check for memory leaks in services
   - Review cache size limits

### Performance Tuning

1. **Database Connection Pool**:
```python
# Adjust in app/core/database.py
engine = create_engine(
    DATABASE_URL,
    pool_size=20,        # Increase for high load
    max_overflow=30,     # Allow temporary connections
    pool_recycle=300     # Recycle connections every 5 minutes
)
```

2. **Redis Configuration**:
```python
# Adjust in app/core/redis_client.py
pool = redis.ConnectionPool(
    max_connections=50,  # Increase for high load
    retry_on_timeout=True,
    health_check_interval=30
)
```

3. **Cache TTL Tuning**:
```python
# Adjust cache TTL based on data volatility
FREQUENT_CACHE_TTL = 1800    # 30 minutes
STABLE_CACHE_TTL = 7200      # 2 hours
STATIC_CACHE_TTL = 86400     # 24 hours
```

## Monitoring and Alerting

Set up monitoring for key performance metrics:

1. **Response Time Alerts**: Alert when average response time > 2s
2. **Error Rate Alerts**: Alert when error rate > 5%
3. **Cache Hit Rate**: Alert when hit rate < 80%
4. **Database Performance**: Alert on slow queries > 1s
5. **Resource Usage**: Alert on high CPU/memory usage

Use the Prometheus metrics endpoint with Grafana for visualization and alerting.