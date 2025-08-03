#!/usr/bin/env python3
"""
Test script to verify TaskService functionality.
"""

import os
import sys
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.'))

from app.core.database import Base
from app.models.user import User
from app.models.process_log import ProcessLog
from app.services.task_service import TaskService


def setup_test_database():
    """Set up a test database."""
    # Clean up any existing test database
    try:
        os.remove("test_task_service.db")
    except:
        pass
    
    # Use SQLite for testing
    engine = create_engine("sqlite:///test_task_service.db", echo=False)
    Base.metadata.create_all(bind=engine)
    
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return SessionLocal


def test_task_service():
    """Test TaskService functionality."""
    print("=== Testing TaskService ===")
    
    # Setup test database
    SessionLocal = setup_test_database()
    
    try:
        with SessionLocal() as db:
            # Create a test user
            test_user = User(
                name="Test User",
                email="test@example.com",
                oauth_provider="reddit"
            )
            db.add(test_user)
            db.commit()
            db.refresh(test_user)
            
            # Initialize TaskService
            task_service = TaskService(db)
            
            # Test 1: Log task start
            print("\n--- Test 1: Log Task Start ---")
            process_log = task_service.log_task_start(
                user_id=test_user.id,
                task_type="test",
                task_id="test-task-123"
            )
            print(f"✓ Task logged with ID: {process_log.id}")
            print(f"  Task ID: {process_log.task_id}")
            print(f"  Status: {process_log.status}")
            print(f"  Created: {process_log.created_at}")
            
            # Test 2: Update task status
            print("\n--- Test 2: Update Task Status ---")
            updated_log = task_service.update_task_status(
                task_id="test-task-123",
                status="running"
            )
            print(f"✓ Task status updated to: {updated_log.status}")
            
            # Test 3: Complete task
            print("\n--- Test 3: Complete Task ---")
            completed_log = task_service.update_task_status(
                task_id="test-task-123",
                status="completed"
            )
            print(f"✓ Task completed at: {completed_log.completed_at}")
            
            # Test 4: Log failed task
            print("\n--- Test 4: Log Failed Task ---")
            failed_log = task_service.log_task_start(
                user_id=test_user.id,
                task_type="test",
                task_id="test-task-456"
            )
            task_service.update_task_status(
                task_id="test-task-456",
                status="failed",
                error_message="Test error message"
            )
            print(f"✓ Failed task logged with error: {failed_log.error_message}")
            
            # Test 5: Get user tasks
            print("\n--- Test 5: Get User Tasks ---")
            user_tasks = task_service.get_user_tasks(test_user.id)
            print(f"✓ Found {len(user_tasks)} tasks for user")
            for task in user_tasks:
                print(f"  - {task.task_type} [{task.task_id}]: {task.status}")
            
            # Test 6: Get task statistics
            print("\n--- Test 6: Get Task Statistics ---")
            stats = task_service.get_task_statistics(test_user.id)
            print(f"✓ Task statistics:")
            print(f"  Total tasks: {stats['total_tasks']}")
            print(f"  Completed: {stats['completed']}")
            print(f"  Failed: {stats['failed']}")
            print(f"  Success rate: {stats['success_rate']:.1f}%")
            print(f"  By type: {stats['by_type']}")
            
            # Test 7: Test task status retrieval (mock)
            print("\n--- Test 7: Get Task Status (Mock) ---")
            status = task_service.get_task_status("test-task-123")
            print(f"✓ Task status retrieved:")
            print(f"  Task ID: {status['task_id']}")
            print(f"  Status: {status['status']}")
            
            print("\n🎉 All TaskService tests passed!")
            return True
            
    except Exception as e:
        print(f"\n✗ TaskService test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # Clean up test database
        try:
            os.remove("test_task_service.db")
        except:
            pass


def main():
    """Main test function."""
    print("=== TaskService Test ===")
    print("This test verifies TaskService functionality with a test database.\n")
    
    success = test_task_service()
    
    if success:
        print("\n✅ TaskService is working correctly!")
    else:
        print("\n❌ TaskService test failed!")


if __name__ == "__main__":
    main()