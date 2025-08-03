# Prometheus Metrics Implementation Guide

## Overview

This document describes the comprehensive Prometheus metrics implementation for the Reddit Content Platform. The system collects metrics across multiple dimensions including API performance, business operations, system resources, and external service interactions.

## Architecture

### Components

1. **FastAPI Middleware** - Collects HTTP request metrics
2. **Celery Task Metrics** - Monitors background task performance
3. **Business Metrics** - Tracks domain-specific operations
4. **System Metrics** - Monitors resource usage
5. **External API Metrics** - Tracks Reddit API interactions

### Metrics Categories

#### API Metrics
- `api_requests_total` - Total HTTP requests by method, endpoint, and status code
- `api_request_duration_seconds` - Request duration histogram
- `api_request_size_bytes` - Request size histogram
- `api_response_size_bytes` - Response size histogram

#### Celery Task Metrics
- `celery_tasks_total` - Total tasks by name, status, and queue
- `celery_task_duration_seconds` - Task execution time histogram
- `celery_task_retries_total` - Task retry count
- `celery_active_tasks` - Currently active tasks by queue

#### Business Metrics
- `crawling_success_rate` - Reddit crawling success percentage by keyword
- `posts_crawled_total` - Total posts crawled by keyword and subreddit
- `content_generated_total` - Content generation count by template and status
- `trend_analysis_total` - Trend analysis operations by keyword and status

#### External API Metrics
- `reddit_api_calls_total` - Reddit API calls by endpoint and status
- `reddit_api_rate_limit_remaining` - Current rate limit remaining
- `reddit_api_response_time_seconds` - Reddit API response time

#### Database Metrics
- `database_connections_total` - Database connections by status
- `database_query_duration_seconds` - Query execution time
- `database_connection_pool_size` - Connection pool size
- `database_connection_pool_active` - Active connections in pool

#### Redis Metrics
- `redis_operations_total` - Redis operations by type and status
- `redis_response_time_seconds` - Redis operation response time
- `redis_cache_hit_rate` - Cache hit rate percentage
- `redis_memory_usage_bytes` - Redis memory usage

#### System Metrics
- `system_cpu_usage_percent` - CPU usage percentage
- `system_memory_usage_bytes` - Memory usage in bytes
- `system_disk_usage_bytes` - Disk usage by path

#### Error Metrics
- `errors_total` - Error count by type and component

## Usage

### Starting the Application with Metrics

The metrics collection starts automatically when the FastAPI application starts:

```bash
# Start the application
uvicorn app.main:app --reload

# Metrics are available at
curl http://localhost:8000/metrics
```

### Monitoring Stack Setup

1. **Start Prometheus and Grafana:**
```bash
docker-compose -f docker-compose.yml -f docker-compose.monitoring.yml up -d
```

2. **Access Dashboards:**
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000 (admin/admin123)
- AlertManager: http://localhost:9093

### Custom Metrics in Code

#### Recording Business Metrics

```python
from app.core.metrics import (
    record_posts_crawled, record_content_generated,
    record_crawling_success_rate
)

# Record crawled posts
record_posts_crawled("python", "programming", 10)

# Record content generation
record_content_generated("blog_post", "success")

# Update success rate
record_crawling_success_rate("python", 95.5)
```

#### Using Celery Task Decorators

```python
from app.core.celery_metrics import business_metrics_task

@celery_app.task
@business_metrics_task
def my_crawling_task(keyword: str):
    # Task implementation
    return {
        "posts_count": 10,
        "subreddit": "programming",
        "success_rate": 95.0
    }
```

#### Recording API Metrics

```python
from app.core.metrics import record_reddit_api_call

# Record Reddit API call
start_time = time.time()
# ... make API call ...
response_time = time.time() - start_time
record_reddit_api_call("search", "success", response_time)
```

## Alerting Rules

### Critical Alerts
- Reddit API rate limit nearly exhausted (< 10 remaining)
- High API error rate (> 10% 5xx errors)
- Database connection failures

### Warning Alerts
- High API latency (95th percentile > 2s)
- Celery task failure rate > 5%
- Low crawling success rate < 80%
- High system resource usage

### Configuration

Alert rules are defined in `monitoring/alert_rules.yml` and can be customized based on your requirements.

## Grafana Dashboards

### Main Dashboard Panels

1. **API Performance**
   - Request rate and error rate
   - Response time percentiles
   - Request/response size distribution

2. **Background Tasks**
   - Celery task success/failure rates
   - Active task counts by queue
   - Task duration histograms

3. **Business Operations**
   - Posts crawled by keyword
   - Content generation rates
   - Crawling success rates

4. **System Resources**
   - CPU and memory usage
   - Redis memory usage
   - Database connection pool status

5. **External Services**
   - Reddit API call rates
   - API response times
   - Rate limit status

### Custom Dashboards

You can create additional dashboards by:

1. Accessing Grafana at http://localhost:3000
2. Creating new dashboard
3. Adding panels with PromQL queries
4. Exporting JSON configuration

## Troubleshooting

### Common Issues

1. **Metrics not appearing:**
   - Check if Prometheus is scraping the `/metrics` endpoint
   - Verify the application is running and accessible
   - Check Prometheus configuration in `monitoring/prometheus.yml`

2. **High cardinality warnings:**
   - Review metric labels to avoid high cardinality
   - Use the endpoint normalization in PrometheusMiddleware
   - Limit dynamic label values

3. **Missing business metrics:**
   - Ensure decorators are applied to Celery tasks
   - Check that metric recording functions are called
   - Verify task return values include expected fields

### Performance Considerations

1. **Metric Collection Overhead:**
   - Metrics collection adds minimal overhead (~1-2ms per request)
   - System metrics are collected every 30 seconds by default
   - Adjust collection intervals based on your needs

2. **Storage Requirements:**
   - Prometheus retains data for 30 days by default
   - Adjust retention in `monitoring/prometheus.yml`
   - Consider using remote storage for long-term retention

## Development

### Adding New Metrics

1. **Define the metric in `app/core/metrics.py`:**
```python
NEW_METRIC = Counter(
    'new_metric_total',
    'Description of new metric',
    ['label1', 'label2'],
    registry=registry
)
```

2. **Create recording function:**
```python
def record_new_metric(label1_value: str, label2_value: str) -> None:
    NEW_METRIC.labels(label1=label1_value, label2=label2_value).inc()
```

3. **Use in application code:**
```python
from app.core.metrics import record_new_metric
record_new_metric("value1", "value2")
```

4. **Add to Grafana dashboard:**
   - Create new panel
   - Use PromQL query: `rate(new_metric_total[5m])`
   - Configure visualization

### Testing Metrics

Run the test script to verify metrics implementation:

```bash
python test_prometheus_metrics.py
```

This will test:
- Basic metric recording
- System metrics collection
- Metrics endpoint functionality
- Business metrics integration

## Security Considerations

1. **Metrics Endpoint Access:**
   - Consider restricting `/metrics` endpoint access
   - Use authentication if exposing publicly
   - Monitor for sensitive data in metric labels

2. **Alert Notifications:**
   - Configure secure channels for alerts
   - Avoid including sensitive data in alert messages
   - Use encrypted communication for webhooks

## Maintenance

### Regular Tasks

1. **Monitor Prometheus storage usage**
2. **Review and update alert thresholds**
3. **Clean up unused metrics**
4. **Update Grafana dashboards**
5. **Test alerting channels**

### Backup and Recovery

1. **Prometheus data:** Located in Docker volume `prometheus_data`
2. **Grafana dashboards:** Export JSON configurations
3. **Configuration files:** Version control all YAML files

## References

- [Prometheus Documentation](https://prometheus.io/docs/)
- [Grafana Documentation](https://grafana.com/docs/)
- [FastAPI Metrics](https://fastapi.tiangolo.com/advanced/middleware/)
- [Celery Monitoring](https://docs.celeryproject.org/en/stable/userguide/monitoring.html)