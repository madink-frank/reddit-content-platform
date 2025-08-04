"""
Celery metrics integration for Prometheus monitoring.
"""

import time
import functools
from typing import Any, Callable
from celery import Task
from celery.signals import (
    task_prerun, task_postrun, task_failure, task_retry,
    task_success, worker_ready, worker_shutdown
)
from app.core.metrics import (
    record_celery_task_start, record_celery_task_success,
    record_celery_task_failure, record_celery_task_retry,
    record_error, CELERY_ACTIVE_TASKS
)


class MetricsTask(Task):
    """Enhanced Celery task class with metrics collection."""
    
    def __init__(self):
        super().__init__()
        self._start_time = None
    
    def __call__(self, *args, **kwargs):
        """Override call to add metrics collection."""
        self._start_time = time.time()
        queue_name = getattr(self.request, 'delivery_info', {}).get('routing_key', 'default')
        
        try:
            # Record task start
            record_celery_task_start(self.name, queue_name)
            
            # Execute task
            result = super().__call__(*args, **kwargs)
            
            # Record success
            duration = time.time() - self._start_time
            record_celery_task_success(self.name, duration, queue_name)
            
            return result
            
        except Exception as exc:
            # Record failure
            duration = time.time() - self._start_time if self._start_time else 0
            record_celery_task_failure(self.name, duration, queue_name)
            record_error(type(exc).__name__, 'celery_task')
            raise
    
    def retry(self, *args, **kwargs):
        """Override retry to record retry metrics."""
        queue_name = getattr(self.request, 'delivery_info', {}).get('routing_key', 'default')
        record_celery_task_retry(self.name, queue_name)
        return super().retry(*args, **kwargs)


def metrics_task(bind=True, base=MetricsTask, **options):
    """Decorator to create a task with metrics collection."""
    def decorator(func):
        return Task.apply_async.__func__(func, bind=bind, base=base, **options)
    return decorator


# Signal handlers for additional metrics
@task_prerun.connect
def task_prerun_handler(sender=None, task_id=None, task=None, args=None, kwargs=None, **kwds):
    """Handle task prerun signal."""
    # Additional setup if needed
    pass


@task_postrun.connect
def task_postrun_handler(sender=None, task_id=None, task=None, args=None, kwargs=None, 
                        retval=None, state=None, **kwds):
    """Handle task postrun signal."""
    # Additional cleanup if needed
    pass


@task_failure.connect
def task_failure_handler(sender=None, task_id=None, exception=None, traceback=None, einfo=None, **kwds):
    """Handle task failure signal."""
    if sender:
        record_error(type(exception).__name__, f'celery_task_{sender.name}')


@task_retry.connect
def task_retry_handler(sender=None, task_id=None, reason=None, einfo=None, **kwds):
    """Handle task retry signal."""
    # Additional retry handling if needed
    pass


@task_success.connect
def task_success_handler(sender=None, result=None, **kwds):
    """Handle task success signal."""
    # Additional success handling if needed
    pass


@worker_ready.connect
def worker_ready_handler(sender=None, **kwds):
    """Handle worker ready signal."""
    # Reset active task counters when worker starts
    for queue in ['crawling', 'analysis', 'content', 'deployment', 'maintenance', 'default']:
        CELERY_ACTIVE_TASKS.labels(queue=queue).set(0)


@worker_shutdown.connect
def worker_shutdown_handler(sender=None, **kwds):
    """Handle worker shutdown signal."""
    # Reset active task counters when worker shuts down
    for queue in ['crawling', 'analysis', 'content', 'deployment', 'maintenance', 'default']:
        CELERY_ACTIVE_TASKS.labels(queue=queue).set(0)


def timed_task(func: Callable) -> Callable:
    """Decorator to time task execution and record metrics."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        task_name = getattr(func, 'name', func.__name__)
        
        try:
            result = func(*args, **kwargs)
            duration = time.time() - start_time
            record_celery_task_success(task_name, duration)
            return result
        except Exception as e:
            duration = time.time() - start_time
            record_celery_task_failure(task_name, duration)
            record_error(type(e).__name__, 'celery_task')
            raise
    
    return wrapper


def business_metrics_task(func: Callable) -> Callable:
    """Decorator to add business-specific metrics to tasks."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        task_name = getattr(func, 'name', func.__name__)
        
        # Import here to avoid circular imports
        from app.core.metrics import (
            record_crawling_success_rate, record_posts_crawled,
            record_content_generated, record_trend_analysis
        )
        
        try:
            result = func(*args, **kwargs)
            
            # Record business metrics based on task type
            if 'crawl' in task_name.lower():
                # Handle crawling metrics
                if isinstance(result, dict) and 'posts_count' in result:
                    keyword = kwargs.get('keyword', 'unknown')
                    subreddit = result.get('subreddit', 'unknown')
                    posts_count = result.get('posts_count', 0)
                    success_rate = result.get('success_rate', 100.0)
                    
                    record_posts_crawled(keyword, subreddit, posts_count)
                    record_crawling_success_rate(keyword, success_rate)
            
            elif 'analyze' in task_name.lower() or 'trend' in task_name.lower():
                # Handle trend analysis metrics
                keyword = kwargs.get('keyword', 'unknown')
                record_trend_analysis(keyword, 'success')
            
            elif 'generate' in task_name.lower() or 'content' in task_name.lower():
                # Handle content generation metrics
                template_type = kwargs.get('template_type', 'default')
                record_content_generated(template_type, 'success')
            
            return result
            
        except Exception as e:
            # Record failure metrics
            if 'analyze' in task_name.lower() or 'trend' in task_name.lower():
                keyword = kwargs.get('keyword', 'unknown')
                record_trend_analysis(keyword, 'failure')
            elif 'generate' in task_name.lower() or 'content' in task_name.lower():
                template_type = kwargs.get('template_type', 'default')
                record_content_generated(template_type, 'failure')
            
            raise
    
    return wrapper