"""
Celery task logging integration with structured logging.
"""

import time
from functools import wraps
from typing import Any, Callable
from celery import Task
from celery.signals import task_prerun, task_postrun, task_failure, task_retry

from app.core.logging import get_logger, set_request_context, clear_request_context, ErrorCategory


logger = get_logger(__name__)


class LoggedTask(Task):
    """Custom Celery task class with structured logging."""
    
    def __call__(self, *args, **kwargs):
        """Execute task with logging context."""
        # Set task context
        task_id = self.request.id if self.request else "unknown"
        correlation_id = kwargs.pop('correlation_id', None)
        
        set_request_context(request_id=correlation_id or task_id)
        
        try:
            return super().__call__(*args, **kwargs)
        finally:
            clear_request_context()


def log_task_execution(func: Callable) -> Callable:
    """Decorator to add structured logging to Celery tasks."""
    
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        task_name = func.__name__
        task_id = self.request.id if hasattr(self, 'request') else "unknown"
        
        # Log task start
        start_time = time.time()
        logger.log_task_start(
            task_name=task_name,
            task_id=task_id,
            args=args[:3] if len(args) > 3 else args,  # Limit args logging
            kwargs={k: v for k, v in kwargs.items() if k not in ['password', 'token', 'secret']}
        )
        
        try:
            # Execute task
            result = func(self, *args, **kwargs)
            
            # Log successful completion
            duration = time.time() - start_time
            logger.log_task_complete(
                task_name=task_name,
                task_id=task_id,
                duration=duration,
                result_type=type(result).__name__ if result is not None else "None"
            )
            
            return result
            
        except Exception as exc:
            # Log task failure
            duration = time.time() - start_time
            logger.log_task_error(
                task_name=task_name,
                task_id=task_id,
                error=exc,
                duration=duration
            )
            raise
    
    return wrapper


# Celery signal handlers for global task logging
@task_prerun.connect
def task_prerun_handler(sender=None, task_id=None, task=None, args=None, kwargs=None, **kwds):
    """Log task start via Celery signals."""
    logger.info(
        f"Task starting: {task.name}",
        operation="celery_task_prerun",
        task_name=task.name,
        task_id=task_id,
        worker_pid=kwds.get('worker_pid'),
        worker_hostname=kwds.get('worker_hostname')
    )


@task_postrun.connect
def task_postrun_handler(sender=None, task_id=None, task=None, args=None, 
                        kwargs=None, retval=None, state=None, **kwds):
    """Log task completion via Celery signals."""
    logger.info(
        f"Task completed: {task.name}",
        operation="celery_task_postrun",
        task_name=task.name,
        task_id=task_id,
        state=state,
        runtime=kwds.get('runtime'),
        worker_hostname=kwds.get('worker_hostname')
    )


@task_failure.connect
def task_failure_handler(sender=None, task_id=None, exception=None, 
                        traceback=None, einfo=None, **kwds):
    """Log task failures via Celery signals."""
    logger.error(
        f"Task failed: {sender.name}",
        operation="celery_task_failure",
        task_name=sender.name,
        task_id=task_id,
        error_message=str(exception),
        error_category=ErrorCategory.CELERY,
        alert_level="medium",
        exc_info=True
    )


@task_retry.connect
def task_retry_handler(sender=None, task_id=None, reason=None, einfo=None, **kwds):
    """Log task retries via Celery signals."""
    logger.warning(
        f"Task retry: {sender.name}",
        operation="celery_task_retry",
        task_name=sender.name,
        task_id=task_id,
        retry_reason=str(reason),
        retry_count=kwds.get('retry_count', 0)
    )


def setup_celery_logging():
    """Setup Celery-specific logging configuration."""
    # This function can be called from celery_app.py to ensure
    # logging is properly configured for Celery workers
    from app.core.logging import setup_logging, configure_advanced_logging
    
    setup_logging()
    configure_advanced_logging()
    
    logger.info("Celery logging configured", operation="celery_logging_setup")