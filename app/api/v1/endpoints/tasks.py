"""
API endpoints for task management and monitoring.
Provides functionality to start, monitor, and manage Celery tasks.
"""

import logging
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.services.task_service import TaskService
from app.workers.crawling_tasks import test_task_with_retry
from app.workers.maintenance_tasks import health_check, cleanup_old_tasks

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/status/{task_id}")
async def get_task_status(
    task_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get the status of a specific task.
    
    Args:
        task_id: The Celery task ID
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Task status information
    """
    try:
        task_service = TaskService(db)
        status = task_service.get_task_status(task_id)
        
        return {
            "success": True,
            "data": status
        }
        
    except Exception as e:
        logger.error(f"Error getting task status for {task_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get task status: {str(e)}")


@router.post("/cancel/{task_id}")
async def cancel_task(
    task_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Cancel a running task.
    
    Args:
        task_id: The Celery task ID
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Cancellation result
    """
    try:
        task_service = TaskService(db)
        result = task_service.cancel_task(task_id)
        
        return {
            "success": True,
            "data": result
        }
        
    except Exception as e:
        logger.error(f"Error cancelling task {task_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to cancel task: {str(e)}")


@router.get("/user-tasks")
async def get_user_tasks(
    task_type: Optional[str] = Query(None, description="Filter by task type"),
    limit: int = Query(50, ge=1, le=100, description="Maximum number of tasks to return"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get tasks for the current user.
    
    Args:
        task_type: Optional filter by task type
        limit: Maximum number of tasks to return
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        List of user tasks
    """
    try:
        task_service = TaskService(db)
        tasks = task_service.get_user_tasks(current_user.id, task_type, limit)
        
        # Convert to dict format for JSON response
        task_data = []
        for task in tasks:
            task_dict = {
                "id": task.id,
                "task_type": task.task_type,
                "status": task.status,
                "task_id": task.task_id,
                "error_message": task.error_message,
                "created_at": task.created_at.isoformat() if task.created_at else None,
                "completed_at": task.completed_at.isoformat() if task.completed_at else None
            }
            task_data.append(task_dict)
        
        return {
            "success": True,
            "data": {
                "tasks": task_data,
                "total": len(task_data)
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting user tasks: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get user tasks: {str(e)}")


@router.get("/statistics")
async def get_task_statistics(
    days: int = Query(7, ge=1, le=365, description="Number of days to include in statistics"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get task execution statistics for the current user.
    
    Args:
        days: Number of days to include in statistics
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Task statistics
    """
    try:
        task_service = TaskService(db)
        stats = task_service.get_task_statistics(current_user.id, days)
        
        return {
            "success": True,
            "data": stats
        }
        
    except Exception as e:
        logger.error(f"Error getting task statistics: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get task statistics: {str(e)}")


@router.post("/test")
async def start_test_task(
    should_fail: bool = Query(False, description="Whether the task should fail to test retry logic"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Start a test task to verify Celery functionality.
    
    Args:
        should_fail: Whether the task should fail to test retry logic
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Task start result
    """
    try:
        # Start the test task
        task_result = test_task_with_retry.delay(should_fail)
        
        # Log the task start
        task_service = TaskService(db)
        process_log = task_service.log_task_start(
            user_id=current_user.id,
            task_type="test",
            task_id=task_result.id
        )
        
        return {
            "success": True,
            "data": {
                "task_id": task_result.id,
                "status": "started",
                "message": "Test task started successfully",
                "should_fail": should_fail,
                "process_log_id": process_log.id
            }
        }
        
    except Exception as e:
        logger.error(f"Error starting test task: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to start test task: {str(e)}")


@router.post("/health-check")
async def start_health_check(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Start a health check task.
    
    Args:
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Health check task start result
    """
    try:
        # Start the health check task
        task_result = health_check.delay()
        
        # Log the task start
        task_service = TaskService(db)
        process_log = task_service.log_task_start(
            user_id=current_user.id,
            task_type="health_check",
            task_id=task_result.id
        )
        
        return {
            "success": True,
            "data": {
                "task_id": task_result.id,
                "status": "started",
                "message": "Health check task started successfully",
                "process_log_id": process_log.id
            }
        }
        
    except Exception as e:
        logger.error(f"Error starting health check task: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to start health check task: {str(e)}")


@router.post("/cleanup")
async def start_cleanup_task(
    days_old: int = Query(30, ge=1, le=365, description="Remove tasks older than this many days"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Start a task cleanup operation.
    
    Args:
        days_old: Remove tasks older than this many days
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Cleanup task start result
    """
    try:
        # Start the cleanup task
        task_result = cleanup_old_tasks.delay(days_old)
        
        # Log the task start
        task_service = TaskService(db)
        process_log = task_service.log_task_start(
            user_id=current_user.id,
            task_type="cleanup",
            task_id=task_result.id
        )
        
        return {
            "success": True,
            "data": {
                "task_id": task_result.id,
                "status": "started",
                "message": f"Cleanup task started - will remove tasks older than {days_old} days",
                "days_old": days_old,
                "process_log_id": process_log.id
            }
        }
        
    except Exception as e:
        logger.error(f"Error starting cleanup task: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to start cleanup task: {str(e)}")


