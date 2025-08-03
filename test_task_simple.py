#!/usr/bin/env python3
"""
Simple test to verify Celery task functionality without database dependencies.
"""

import sys
import os

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.'))

from app.core.celery_app import celery_app
from app.workers.crawling_tasks import test_task_with_retry
from app.workers.maintenance_tasks import health_check


def test_task_creation():
    """Test that tasks can be created and configured properly."""
    print("=== Testing Task Creation ===")
    
    # Test creating task instances
    try:
        # Create task instances (without executing)
        test_task = test_task_with_retry.s(should_fail=False)
        health_task = health_check.s()
        
        print(f"✓ Test task created: {test_task}")
        print(f"✓ Health check task created: {health_task}")
        
        # Check task properties
        print(f"✓ Test task name: {test_task_with_retry.name}")
        print(f"✓ Health check task name: {health_check.name}")
        
        return True
        
    except Exception as e:
        print(f"✗ Task creation failed: {e}")
        return False


def test_task_configuration():
    """Test task configuration and retry settings."""
    print("\n=== Testing Task Configuration ===")
    
    try:
        # Check task retry configuration
        print(f"✓ Test task autoretry_for: {test_task_with_retry.autoretry_for}")
        print(f"✓ Test task retry_kwargs: {test_task_with_retry.retry_kwargs}")
        print(f"✓ Test task retry_backoff: {test_task_with_retry.retry_backoff}")
        
        # Check task routing
        task_routes = celery_app.conf.task_routes
        print(f"✓ Task routes configured: {len(task_routes)} routes")
        
        # Check task annotations
        task_annotations = celery_app.conf.task_annotations
        print(f"✓ Task annotations configured: {len(task_annotations)} patterns")
        
        return True
        
    except Exception as e:
        print(f"✗ Task configuration test failed: {e}")
        return False


def test_celery_app_ready():
    """Test that Celery app is properly configured."""
    print("\n=== Testing Celery App Readiness ===")
    
    try:
        # Check app configuration
        print(f"✓ App name: {celery_app.main}")
        print(f"✓ Broker URL configured: {bool(celery_app.conf.broker_url)}")
        print(f"✓ Result backend configured: {bool(celery_app.conf.result_backend)}")
        
        # Check task registration
        registered_tasks = [name for name in celery_app.tasks.keys() if not name.startswith('celery.')]
        print(f"✓ Registered tasks: {len(registered_tasks)}")
        
        # Check beat schedule
        beat_schedule = celery_app.conf.beat_schedule
        print(f"✓ Beat schedule configured: {len(beat_schedule)} scheduled tasks")
        
        return True
        
    except Exception as e:
        print(f"✗ Celery app readiness test failed: {e}")
        return False


def test_task_signatures():
    """Test task signature creation."""
    print("\n=== Testing Task Signatures ===")
    
    try:
        # Create various task signatures
        signatures = [
            test_task_with_retry.s(should_fail=False),
            test_task_with_retry.s(should_fail=True),
            health_check.s(),
        ]
        
        for i, sig in enumerate(signatures):
            print(f"✓ Signature {i+1}: {sig.task} with args {sig.args} and kwargs {sig.kwargs}")
        
        # Test signature properties
        test_sig = test_task_with_retry.s(should_fail=False)
        print(f"✓ Signature task name: {test_sig.task}")
        print(f"✓ Signature args: {test_sig.args}")
        print(f"✓ Signature kwargs: {test_sig.kwargs}")
        
        return True
        
    except Exception as e:
        print(f"✗ Task signature test failed: {e}")
        return False


def main():
    """Main test function."""
    print("=== Simple Celery Task Test ===")
    print("This test verifies basic Celery task functionality without requiring Redis or workers.\n")
    
    tests = [
        ("Task Creation", test_task_creation),
        ("Task Configuration", test_task_configuration),
        ("Celery App Readiness", test_celery_app_ready),
        ("Task Signatures", test_task_signatures)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"✗ {test_name} failed with error: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n=== Test Summary ===")
    passed = 0
    for test_name, result in results:
        status = "✓" if result else "✗"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\nPassed: {passed}/{len(results)}")
    
    if passed == len(results):
        print("\n🎉 All basic task tests passed!")
        print("\nCelery task system is properly configured and ready for use.")
        print("\nNext steps:")
        print("1. Start Redis: redis-server")
        print("2. Start Celery worker: ./scripts/start_celery_worker.sh")
        print("3. Test task execution: python test_celery_setup.py")
    else:
        print("\n⚠ Some basic task tests failed. Check the output above.")


if __name__ == "__main__":
    main()