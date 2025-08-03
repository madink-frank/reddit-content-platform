#!/usr/bin/env python3
"""
Test script for Prometheus metrics implementation.
"""

import asyncio
import time
import requests
from app.core.metrics import (
    REQUEST_COUNT, REQUEST_DURATION, CELERY_TASK_COUNT,
    record_celery_task_start, record_celery_task_success,
    record_reddit_api_call, record_database_connection,
    record_redis_operation, update_system_metrics,
    get_metrics_response
)


def test_basic_metrics():
    """Test basic metrics collection."""
    print("Testing basic metrics collection...")
    
    # Test API metrics
    REQUEST_COUNT.labels(method="GET", endpoint="/test", status_code=200).inc()
    REQUEST_DURATION.labels(method="GET", endpoint="/test").observe(0.5)
    
    # Test Celery metrics
    record_celery_task_start("test_task", "test_queue")
    record_celery_task_success("test_task", 2.5, "test_queue")
    
    # Test external API metrics
    record_reddit_api_call("search", "success", 1.2)
    
    # Test database metrics
    record_database_connection("success")
    
    # Test Redis metrics
    record_redis_operation("get", "success", 0.01)
    
    print("✓ Basic metrics recorded successfully")


def test_system_metrics():
    """Test system metrics collection."""
    print("Testing system metrics collection...")
    
    try:
        update_system_metrics()
        print("✓ System metrics updated successfully")
    except Exception as e:
        print(f"✗ System metrics failed: {e}")


def test_metrics_endpoint():
    """Test metrics endpoint response."""
    print("Testing metrics endpoint...")
    
    try:
        response = get_metrics_response()
        content = response.body.decode('utf-8')
        
        # Check for expected metrics
        expected_metrics = [
            'api_requests_total',
            'celery_tasks_total',
            'reddit_api_calls_total',
            'database_connections_total',
            'redis_operations_total'
        ]
        
        for metric in expected_metrics:
            if metric in content:
                print(f"✓ Found metric: {metric}")
            else:
                print(f"✗ Missing metric: {metric}")
        
        print("✓ Metrics endpoint working")
        
    except Exception as e:
        print(f"✗ Metrics endpoint failed: {e}")


async def test_api_endpoint():
    """Test API endpoint with metrics."""
    print("Testing API endpoint with metrics...")
    
    try:
        # This would normally be done by starting the FastAPI server
        # For now, just test the middleware logic
        from app.core.metrics import PrometheusMiddleware
        from fastapi import Request, Response
        from unittest.mock import Mock
        
        middleware = PrometheusMiddleware()
        
        # Mock request and response
        request = Mock()
        request.url.path = "/test"
        request.method = "GET"
        request.headers = {}
        
        response = Mock()
        response.status_code = 200
        response.headers = {}
        
        async def mock_call_next(req):
            await asyncio.sleep(0.1)  # Simulate processing time
            return response
        
        # Test middleware
        result = await middleware(request, mock_call_next)
        
        print("✓ Middleware processed request successfully")
        
    except Exception as e:
        print(f"✗ API endpoint test failed: {e}")


def test_business_metrics():
    """Test business-specific metrics."""
    print("Testing business metrics...")
    
    try:
        from app.core.metrics import (
            record_crawling_success_rate, record_posts_crawled,
            record_content_generated, record_trend_analysis
        )
        
        # Test crawling metrics
        record_crawling_success_rate("python", 95.5)
        record_posts_crawled("python", "programming", 10)
        
        # Test content generation metrics
        record_content_generated("blog_post", "success")
        
        # Test trend analysis metrics
        record_trend_analysis("python", "success")
        
        print("✓ Business metrics recorded successfully")
        
    except Exception as e:
        print(f"✗ Business metrics failed: {e}")


def main():
    """Run all tests."""
    print("=== Prometheus Metrics Test Suite ===\n")
    
    test_basic_metrics()
    test_system_metrics()
    test_metrics_endpoint()
    test_business_metrics()
    
    # Run async test
    asyncio.run(test_api_endpoint())
    
    print("\n=== Test Summary ===")
    print("Metrics implementation test completed.")
    print("Check the output above for any failures.")
    
    # Show sample metrics output
    print("\n=== Sample Metrics Output ===")
    try:
        response = get_metrics_response()
        content = response.body.decode('utf-8')
        lines = content.split('\n')[:20]  # Show first 20 lines
        for line in lines:
            if line.strip():
                print(line)
        print("... (truncated)")
    except Exception as e:
        print(f"Could not display metrics: {e}")


if __name__ == "__main__":
    main()