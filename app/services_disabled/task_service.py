"""
Task status tracking and management service.
Provides functionality to track Celery task status and results.
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from celery.result import AsyncResult
from celery import states

from app.core.celery_app import celery_app
from app.core.database import get_db
from app.models.process_log import ProcessLog

logger = logging.getLogger(__name__)


class TaskService:
    """Service for managing and tracking Celery tasks."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """
        Get the current status of a Celery task.
        
        Args:
            task_id: The Celery task ID
            
        Returns:
            Dictionary containing task status information
        """
        try:
            result = AsyncResult(task_id, app=celery_app)
            
            status_info = {
                "task_id": task_id,
                "status": result.status,
                "ready": result.ready(),
                "successful": result.successful() if result.ready() else None,
                "failed": result.failed() if result.ready() else None,
                "result": None,
                "error": None,
                "traceback": None,
                "progress": None
            }
            
            if result.ready():
                if result.successful():
                    status_info["result"] = result.result
                elif result.failed():
                    status_info["error"] = str(result.result)
                    status_info["traceback"] = result.traceback
            else:
                # Check for progress information
                if hasattr(result, 'info') and result.info:
                    if isinstance(result.info, dict):
                        status_info["progress"] = result.info.get('progress')
                        status_info["current"] = result.info.get('current')
                        status_info["total"] = result.info.get('total')
                        status_info["status_message"] = result.info.get('status')
            
            return status_info
            
        except Exception as e:
            logger.error(f"Error getting task status for {task_id}: {e}")
            return {
                "task_id": task_id,
                "status": "ERROR",
                "error": f"Failed to get task status: {str(e)}"
            }
    
    def cancel_task(self, task_id: str) -> Dict[str, Any]:
        """
        Cancel a running Celery task.
        
        Args:
            task_id: The Celery task ID
            
        Returns:
            Dictionary containing cancellation result
        """
        try:
            celery_app.control.revoke(task_id, terminate=True)
            
            # Update process log if exists
            process_log = self.db.query(ProcessLog).filter(
                ProcessLog.task_id == task_id
            ).first()
            
            if process_log:
                process_log.status = "cancelled"
                process_log.completed_at = datetime.utcnow()
                process_log.error_message = "Task cancelled by user"
                self.db.commit()
            
            return {
                "task_id": task_id,
                "status": "cancelled",
                "message": "Task cancellation requested"
            }
            
        except Exception as e:
            logger.error(f"Error cancelling task {task_id}: {e}")
            return {
                "task_id": task_id,
                "status": "error",
                "error": f"Failed to cancel task: {str(e)}"
            }
    
    def log_task_start(self, user_id: int, task_type: str, task_id: str) -> ProcessLog:
        """
        Log the start of a task in the database.
        
        Args:
            user_id: ID of the user who initiated the task
            task_type: Type of task (e.g., 'crawling', 'analysis')
            task_id: The Celery task ID
            
        Returns:
            ProcessLog instance
        """
        try:
            process_log = ProcessLog(
                user_id=user_id,
                task_type=task_type,
                status="pending",
                task_id=task_id,
                created_at=datetime.utcnow()
            )
            
            self.db.add(process_log)
            self.db.commit()
            self.db.refresh(process_log)
            
            logger.info(f"Logged task start: {task_type} [{task_id}] for user {user_id}")
            return process_log
            
        except Exception as e:
            logger.error(f"Error logging task start: {e}")
            self.db.rollback()
            raise
    
    def update_task_status(self, task_id: str, status: str, 
                          error_message: Optional[str] = None) -> Optional[ProcessLog]:
        """
        Update the status of a task in the database.
        
        Args:
            task_id: The Celery task ID
            status: New status ('running', 'completed', 'failed', 'cancelled')
            error_message: Error message if task failed
            
        Returns:
            Updated ProcessLog instance or None if not found
        """
        try:
            process_log = self.db.query(ProcessLog).filter(
                ProcessLog.task_id == task_id
            ).first()
            
            if not process_log:
                logger.warning(f"Process log not found for task {task_id}")
                return None
            
            process_log.status = status
            if error_message:
                process_log.error_message = error_message
            
            if status in ["completed", "failed", "cancelled"]:
                process_log.completed_at = datetime.utcnow()
            
            self.db.commit()
            self.db.refresh(process_log)
            
            logger.info(f"Updated task status: {task_id} -> {status}")
            return process_log
            
        except Exception as e:
            logger.error(f"Error updating task status: {e}")
            self.db.rollback()
            return None
    
    def get_user_tasks(self, user_id: int, task_type: Optional[str] = None, 
                      limit: int = 50) -> List[ProcessLog]:
        """
        Get tasks for a specific user.
        
        Args:
            user_id: ID of the user
            task_type: Optional filter by task type
            limit: Maximum number of tasks to return
            
        Returns:
            List of ProcessLog instances
        """
        try:
            query = self.db.query(ProcessLog).filter(ProcessLog.user_id == user_id)
            
            if task_type:
                query = query.filter(ProcessLog.task_type == task_type)
            
            tasks = query.order_by(ProcessLog.created_at.desc()).limit(limit).all()
            
            return tasks
            
        except Exception as e:
            logger.error(f"Error getting user tasks: {e}")
            return []
    
    def cleanup_old_tasks(self, days_old: int = 30) -> int:
        """
        Clean up old completed tasks from the database.
        
        Args:
            days_old: Remove tasks older than this many days
            
        Returns:
            Number of tasks removed
        """
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days_old)
            
            deleted_count = self.db.query(ProcessLog).filter(
                ProcessLog.completed_at < cutoff_date,
                ProcessLog.status.in_(["completed", "failed", "cancelled"])
            ).delete()
            
            self.db.commit()
            
            logger.info(f"Cleaned up {deleted_count} old tasks")
            return deleted_count
            
        except Exception as e:
            logger.error(f"Error cleaning up old tasks: {e}")
            self.db.rollback()
            return 0
    
    def get_task_statistics(self, user_id: Optional[int] = None, 
                           days: int = 7) -> Dict[str, Any]:
        """
        Get task execution statistics.
        
        Args:
            user_id: Optional filter by user ID
            days: Number of days to include in statistics
            
        Returns:
            Dictionary containing task statistics
        """
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            query = self.db.query(ProcessLog).filter(
                ProcessLog.created_at >= cutoff_date
            )
            
            if user_id:
                query = query.filter(ProcessLog.user_id == user_id)
            
            tasks = query.all()
            
            stats = {
                "total_tasks": len(tasks),
                "completed": len([t for t in tasks if t.status == "completed"]),
                "failed": len([t for t in tasks if t.status == "failed"]),
                "running": len([t for t in tasks if t.status == "running"]),
                "pending": len([t for t in tasks if t.status == "pending"]),
                "cancelled": len([t for t in tasks if t.status == "cancelled"]),
                "by_type": {}
            }
            
            # Group by task type
            for task in tasks:
                task_type = task.task_type
                if task_type not in stats["by_type"]:
                    stats["by_type"][task_type] = {
                        "total": 0,
                        "completed": 0,
                        "failed": 0,
                        "running": 0,
                        "pending": 0,
                        "cancelled": 0
                    }
                
                stats["by_type"][task_type]["total"] += 1
                stats["by_type"][task_type][task.status] += 1
            
            # Calculate success rate
            if stats["total_tasks"] > 0:
                stats["success_rate"] = (stats["completed"] / stats["total_tasks"]) * 100
            else:
                stats["success_rate"] = 0
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting task statistics: {e}")
            return {
                "total_tasks": 0,
                "completed": 0,
                "failed": 0,
                "running": 0,
                "pending": 0,
                "cancelled": 0,
                "by_type": {},
                "success_rate": 0
            }


def get_task_service(db: Session = next(get_db())) -> TaskService:
    """Dependency to get TaskService instance."""
    return TaskService(db)