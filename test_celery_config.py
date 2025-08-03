#!/usr/bin/env python3
"""
Test script to verify Celery configuration without requiring Redis to be running.
"""

from app.core.celery_app import celery_app, BaseTask
from app.workers import crawling_tasks, analysis_tasks, content_tasks, deployment_tasks, maintenance_tasks


def test_celery_app_configuration():
    """Test Celery app configuration."""
    print("=== Testing Celery App Configuration ===")
    
    # Test basic configuration
    print(f"✓ App name: {celery_app.main}")
    print(f"✓ Broker URL: {celery_app.conf.broker_url}")
    print(f"✓ Result backend: {celery_app.conf.result_backend}")
    print(f"✓ Task serializer: {celery_app.conf.task_serializer}")
    print(f"✓ Result serializer: {celery_app.conf.result_serializer}")
    
    # Test task routing
    print("\n--- Task Routing ---")
    for pattern, route in celery_app.conf.task_routes.items():
        print(f"✓ {pattern} -> {route}")
    
    # Test task annotations
    print("\n--- Task Annotations ---")
    for pattern, annotations in celery_app.conf.task_annotations.items():
        print(f"✓ {pattern}:")
        for key, value in annotations.items():
            print(f"    {key}: {value}")
    
    return True


def test_task_registration():
    """Test that tasks are properly registered."""
    print("\n=== Testing Task Registration ===")
    
    registered_tasks = list(celery_app.tasks.keys())
    registered_tasks.sort()
    
    expected_tasks = [
        'crawl_trending_keywords',
        'crawl_keyword_posts',
        'test_task_with_retry',
        'analyze_keyword_trends',
        'analyze_single_keyword',
        'generate_blog_content',
        'generate_multiple_content',
        'deploy_to_vercel',
        'deploy_to_netlify',
        'deploy_content',
        'cleanup_old_data',
        'cleanup_old_tasks',
        'health_check'
    ]
    
    print(f"Total registered tasks: {len(registered_tasks)}")
    
    # Check expected tasks
    missing_tasks = []
    for task_name in expected_tasks:
        full_task_name = f"app.workers.{task_name}" if not task_name.startswith('app.') else task_name
        
        # Check various possible task name formats
        found = False
        for registered_task in registered_tasks:
            if task_name in registered_task or registered_task.endswith(task_name):
                print(f"✓ {task_name} -> {registered_task}")
                found = True
                break
        
        if not found:
            missing_tasks.append(task_name)
            print(f"✗ {task_name} (not found)")
    
    if missing_tasks:
        print(f"\n⚠ Missing tasks: {missing_tasks}")
    else:
        print("\n✓ All expected tasks are registered")
    
    # Show all registered tasks
    print("\n--- All Registered Tasks ---")
    for task in registered_tasks:
        if not task.startswith('celery.'):  # Skip built-in Celery tasks
            print(f"  - {task}")
    
    return len(missing_tasks) == 0


def test_base_task_class():
    """Test the custom BaseTask class."""
    print("\n=== Testing BaseTask Class ===")
    
    # Check if BaseTask is properly configured
    print(f"✓ Default task class: {celery_app.Task}")
    print(f"✓ BaseTask autoretry_for: {BaseTask.autoretry_for}")
    print(f"✓ BaseTask retry_kwargs: {BaseTask.retry_kwargs}")
    print(f"✓ BaseTask retry_backoff: {BaseTask.retry_backoff}")
    print(f"✓ BaseTask retry_backoff_max: {BaseTask.retry_backoff_max}")
    
    return True


def test_beat_schedule():
    """Test Celery Beat schedule configuration."""
    print("\n=== Testing Beat Schedule ===")
    
    beat_schedule = celery_app.conf.beat_schedule
    
    if beat_schedule:
        print(f"✓ Beat schedule configured with {len(beat_schedule)} tasks:")
        for task_name, config in beat_schedule.items():
            print(f"  - {task_name}:")
            print(f"    Task: {config['task']}")
            print(f"    Schedule: {config['schedule']} seconds")
    else:
        print("✗ No beat schedule configured")
        return False
    
    return True


def main():
    """Main test function."""
    print("=== Celery Configuration Test ===")
    print("This test verifies Celery configuration without requiring Redis/RabbitMQ to be running.\n")
    
    tests = [
        ("App Configuration", test_celery_app_configuration),
        ("Task Registration", test_task_registration),
        ("BaseTask Class", test_base_task_class),
        ("Beat Schedule", test_beat_schedule)
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
        print("\n🎉 All configuration tests passed!")
        print("\nTo test actual task execution:")
        print("1. Start Redis: redis-server")
        print("2. Start Celery worker: ./scripts/start_celery_worker.sh")
        print("3. Run execution test: python test_celery_setup.py")
    else:
        print("\n⚠ Some configuration tests failed. Check the output above.")


if __name__ == "__main__":
    main()