"""
Celery application configuration for background task processing.
Handles Reddit crawling, trend analysis, and content generation tasks.
"""

import logging
from celery import Celery
from celery.signals import task_prerun, task_postrun, task_failure, task_retry
from app.core.config import settings
from app.core.celery_logging import setup_celery_logging, LoggedTask

# Setup structured logging for Celery
setup_celery_logging()
logger = logging.getLogger(__name__)

# Create Celery app instance
celery_app = Celery(
    "reddit_content_platform",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=[
        "app.workers.crawling_tasks",
        "app.workers.analysis_tasks", 
        "app.workers.content_tasks",
        "app.workers.deployment_tasks",
        "app.workers.maintenance_tasks"
    ]
)

# Celery configuration
celery_app.conf.update(
    # Task routing
    task_routes={
        "app.workers.crawling_tasks.*": {"queue": "crawling"},
        "app.workers.analysis_tasks.*": {"queue": "analysis"},
        "app.workers.content_tasks.*": {"queue": "content"},
        "app.workers.deployment_tasks.*": {"queue": "deployment"},
        "app.workers.maintenance_tasks.*": {"queue": "maintenance"},
    },
    
    # Task serialization
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    
    # Task execution
    task_always_eager=settings.ENVIRONMENT == "test",
    task_eager_propagates=True,
    
    # Result backend settings
    result_expires=3600,  # 1 hour
    result_persistent=True,
    result_backend_transport_options={
        'master_name': 'mymaster',
        'visibility_timeout': 3600,
    },
    
    # Worker settings
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
    worker_disable_rate_limits=False,
    
    # Retry settings
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    task_default_retry_delay=60,  # 1 minute
    task_max_retries=3,
    
    # Task tracking
    task_track_started=True,
    task_send_sent_event=True,
    
    # Timezone
    timezone="UTC",
    enable_utc=True,
    
    # Error handling
    task_annotations={
        '*': {
            'rate_limit': '10/s',
            'time_limit': 300,  # 5 minutes hard limit
            'soft_time_limit': 240,  # 4 minutes soft limit
        },
        'app.workers.crawling_tasks.*': {
            'rate_limit': '5/s',
            'time_limit': 600,  # 10 minutes for crawling tasks
            'soft_time_limit': 540,
        },
        'app.workers.analysis_tasks.*': {
            'rate_limit': '3/s',
            'time_limit': 900,  # 15 minutes for analysis tasks
            'soft_time_limit': 840,
        },
    },
    
    # Beat schedule for periodic tasks
    beat_schedule={
        "crawl-trending-keywords": {
            "task": "app.workers.crawling_tasks.crawl_trending_keywords",
            "schedule": 3600.0,  # Every hour
        },
        "analyze-trends": {
            "task": "app.workers.analysis_tasks.analyze_keyword_trends",
            "schedule": 1800.0,  # Every 30 minutes
        },
        "cleanup-old-data": {
            "task": "app.workers.maintenance_tasks.cleanup_old_data",
            "schedule": 86400.0,  # Daily
        },
    },
)

# Import metrics integration
from app.core.celery_metrics import MetricsTask

# Task status tracking and logging signals
@task_prerun.connect
def task_prerun_handler(sender=None, task_id=None, task=None, args=None, kwargs=None, **kwds):
    """Log task start and update status."""
    logger.info(f"Task {task.name} [{task_id}] started with args: {args}, kwargs: {kwargs}")


@task_postrun.connect
def task_postrun_handler(sender=None, task_id=None, task=None, args=None, kwargs=None, 
                        retval=None, state=None, **kwds):
    """Log task completion and update status."""
    logger.info(f"Task {task.name} [{task_id}] completed with state: {state}, result: {retval}")


@task_failure.connect
def task_failure_handler(sender=None, task_id=None, exception=None, traceback=None, einfo=None, **kwds):
    """Log task failure and update status."""
    logger.error(f"Task {sender.name} [{task_id}] failed with exception: {exception}")
    logger.error(f"Traceback: {traceback}")


@task_retry.connect
def task_retry_handler(sender=None, task_id=None, reason=None, einfo=None, **kwds):
    """Log task retry attempts."""
    logger.warning(f"Task {sender.name} [{task_id}] retrying due to: {reason}")


# Enhanced task base class with metrics and error handling
class BaseTask(MetricsTask):
    """Base task class with metrics collection, error handling and retry logic."""
    
    autoretry_for = (Exception,)
    retry_kwargs = {'max_retries': 3, 'countdown': 60}
    retry_backoff = True
    retry_backoff_max = 700
    retry_jitter = False
    
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """Called when task fails after all retries."""
        logger.error(f"Task {self.name} [{task_id}] failed permanently: {exc}")
        # Metrics are already recorded in MetricsTask
        
    def on_retry(self, exc, task_id, args, kwargs, einfo):
        """Called when task is retried."""
        logger.warning(f"Task {self.name} [{task_id}] retrying: {exc}")
        # Metrics are already recorded in MetricsTask
        
    def on_success(self, retval, task_id, args, kwargs):
        """Called when task succeeds."""
        logger.info(f"Task {self.name} [{task_id}] succeeded with result: {retval}")
        # Metrics are already recorded in MetricsTask


# Set the default task base class with structured logging
celery_app.Task = LoggedTask