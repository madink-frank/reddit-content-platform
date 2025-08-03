#!/usr/bin/env python3
"""
Test script to verify Celery setup and task execution.
"""

import asyncio
import time
from app.core.celery_app import celery_app
from app.workers.crawling_tasks import test_task_with_retry
from app.workers.maintenance_tasks import health_check


def test_celery_connection():
    """Test basic Celery connection."""
    print("Testing Celery connection...")
    
    try:
        # Test broker connection
        inspect = celery_app.control.inspect()
        stats = inspect.stats()
        
        if stats:
            print("✓ Celery broker connection successful")
            print(f"  Active workers: {len(stats)}")
            for worker, info in stats.items():
                print(f"    - {worker}: {info.get('pool', {}).get('max-concurrency', 'unknown')} processes")
        else:
            print("⚠ No active workers found")
            
    except Exception as e:
        print(f"✗ Celery broker connection failed: {e}")
        return False
    
    return True


def test_task_execution():
    """Test task execution."""
    print("\nTesting task execution...")
    
    try:
        # Start a test task
        print("Starting test task...")
        result = test_task_with_retry.delay(should_fail=False)
        print(f"Task started with ID: {result.id}")
        
        # Wait for completion (with timeout)
        timeout = 30
        start_time = time.time()
        
        while not result.ready() and (time.time() - start_time) < timeout:
            print(f"Task status: {result.status}")
            time.sleep(2)
        
        if result.ready():
            if result.successful():
                print(f"✓ Task completed successfully: {result.result}")
                return True
            else:
                print(f"✗ Task failed: {result.result}")
                return False
        else:
            print("✗ Task timed out")
            return False
            
    except Exception as e:
        print(f"✗ Task execution failed: {e}")
        return False


def test_health_check():
    """Test health check task."""
    print("\nTesting health check task...")
    
    try:
        # Start health check task
        print("Starting health check task...")
        result = health_check.delay()
        print(f"Health check task started with ID: {result.id}")
        
        # Wait for completion
        timeout = 30
        start_time = time.time()
        
        while not result.ready() and (time.time() - start_time) < timeout:
            print(f"Health check status: {result.status}")
            time.sleep(2)
        
        if result.ready():
            if result.successful():
                health_result = result.result
                print(f"✓ Health check completed: {health_result['status']}")
                print("Component status:")
                for component, status in health_result['components'].items():
                    print(f"  - {component}: {status}")
                return True
            else:
                print(f"✗ Health check failed: {result.result}")
                return False
        else:
            print("✗ Health check timed out")
            return False
            
    except Exception as e:
        print(f"✗ Health check failed: {e}")
        return False


def main():
    """Main test function."""
    print("=== Celery Setup Test ===")
    
    # Test connection
    connection_ok = test_celery_connection()
    
    if not connection_ok:
        print("\n❌ Celery connection test failed. Make sure Redis is running and Celery worker is started.")
        print("\nTo start a Celery worker, run:")
        print("  celery -A app.core.celery_app worker --loglevel=info")
        return
    
    # Test task execution
    execution_ok = test_task_execution()
    
    # Test health check
    health_ok = test_health_check()
    
    # Summary
    print("\n=== Test Summary ===")
    print(f"Connection: {'✓' if connection_ok else '✗'}")
    print(f"Task Execution: {'✓' if execution_ok else '✗'}")
    print(f"Health Check: {'✓' if health_ok else '✗'}")
    
    if connection_ok and execution_ok and health_ok:
        print("\n🎉 All tests passed! Celery setup is working correctly.")
    else:
        print("\n⚠ Some tests failed. Check the output above for details.")


if __name__ == "__main__":
    main()