"""
Structured logging system with JSON formatting, request tracking, and error classification.
"""

import logging
import logging.config
import json
import sys
import traceback
import uuid
import asyncio
import time
import functools
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List
from enum import Enum
from contextvars import ContextVar
from app.core.config import settings


# Context variables for request tracking
request_id_var: ContextVar[Optional[str]] = ContextVar('request_id', default=None)
user_id_var: ContextVar[Optional[int]] = ContextVar('user_id', default=None)


class LogLevel(str, Enum):
    """Log level enumeration."""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class ErrorCategory(str, Enum):
    """Error categorization for alerting."""
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    VALIDATION = "validation"
    EXTERNAL_API = "external_api"
    DATABASE = "database"
    REDIS = "redis"
    CELERY = "celery"
    SYSTEM = "system"
    BUSINESS_LOGIC = "business_logic"
    UNKNOWN = "unknown"


class JSONFormatter(logging.Formatter):
    """Enhanced JSON formatter for structured logging."""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as structured JSON."""
        # Base log entry
        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
            "thread": record.thread,
            "thread_name": record.threadName,
            "process": record.process,
        }
        
        # Add request context
        request_id = request_id_var.get()
        if request_id:
            log_entry["request_id"] = request_id
        
        user_id = user_id_var.get()
        if user_id:
            log_entry["user_id"] = user_id
        
        # Add custom fields from record
        for attr in ["request_id", "user_id", "correlation_id", "operation", 
                     "duration", "status_code", "error_category", "alert_level"]:
            if hasattr(record, attr):
                log_entry[attr] = getattr(record, attr)
        
        # Add exception information
        if record.exc_info and record.exc_info != (None, None, None) and not isinstance(record.exc_info, bool):
            exc_type, exc_value, exc_traceback = record.exc_info
            log_entry["exception"] = {
                "type": exc_type.__name__ if exc_type else None,
                "message": str(exc_value) if exc_value else None,
                "traceback": self.formatException(record.exc_info)
            }
        
        # Add stack trace for errors
        if record.levelno >= logging.ERROR and not record.exc_info:
            log_entry["stack_trace"] = self.formatStack(record.stack_info) if record.stack_info else None
        
        # Add environment context
        log_entry["environment"] = settings.ENVIRONMENT
        log_entry["service"] = settings.PROJECT_NAME
        log_entry["version"] = settings.VERSION
        
        return json.dumps(log_entry, ensure_ascii=False)


class StructuredLogger:
    """Enhanced logger with structured logging capabilities."""
    
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
    
    def _log_with_context(self, level: int, message: str, **kwargs):
        """Log with additional context."""
        extra = {}
        
        # Add context variables
        if request_id_var.get():
            extra["request_id"] = request_id_var.get()
        if user_id_var.get():
            extra["user_id"] = user_id_var.get()
        
        # Handle exc_info separately to avoid conflicts
        exc_info = kwargs.pop('exc_info', None)
        
        # Add custom fields
        for key, value in kwargs.items():
            extra[key] = value
        
        self.logger.log(level, message, extra=extra, exc_info=exc_info)
    
    def debug(self, message: str, **kwargs):
        """Log debug message."""
        self._log_with_context(logging.DEBUG, message, **kwargs)
    
    def info(self, message: str, **kwargs):
        """Log info message."""
        self._log_with_context(logging.INFO, message, **kwargs)
    
    def warning(self, message: str, **kwargs):
        """Log warning message."""
        self._log_with_context(logging.WARNING, message, **kwargs)
    
    def error(self, message: str, error_category: ErrorCategory = ErrorCategory.UNKNOWN, 
              alert_level: str = "low", **kwargs):
        """Log error message with categorization."""
        # Handle both ErrorCategory enum and string values
        if isinstance(error_category, ErrorCategory):
            error_category_value = error_category.value
        else:
            error_category_value = error_category
            
        kwargs.update({
            "error_category": error_category_value,
            "alert_level": alert_level
        })
        self._log_with_context(logging.ERROR, message, **kwargs)
    
    def critical(self, message: str, error_category: ErrorCategory = ErrorCategory.SYSTEM,
                 alert_level: str = "high", **kwargs):
        """Log critical message with high alert level."""
        # Handle both ErrorCategory enum and string values
        if isinstance(error_category, ErrorCategory):
            error_category_value = error_category.value
        else:
            error_category_value = error_category
            
        kwargs.update({
            "error_category": error_category_value,
            "alert_level": alert_level
        })
        self._log_with_context(logging.CRITICAL, message, **kwargs)
    
    def log_request(self, method: str, path: str, status_code: int, 
                   duration: float, **kwargs):
        """Log HTTP request with structured data."""
        self.info(
            f"{method} {path} - {status_code}",
            operation="http_request",
            method=method,
            path=path,
            status_code=status_code,
            duration=duration,
            **kwargs
        )
    
    def log_task_start(self, task_name: str, task_id: str, **kwargs):
        """Log Celery task start."""
        self.info(
            f"Task started: {task_name}",
            operation="task_start",
            task_name=task_name,
            task_id=task_id,
            **kwargs
        )
    
    def log_task_complete(self, task_name: str, task_id: str, 
                         duration: float, **kwargs):
        """Log Celery task completion."""
        self.info(
            f"Task completed: {task_name}",
            operation="task_complete",
            task_name=task_name,
            task_id=task_id,
            duration=duration,
            **kwargs
        )
    
    def log_task_error(self, task_name: str, task_id: str, error: Exception, **kwargs):
        """Log Celery task error."""
        self.error(
            f"Task failed: {task_name} - {str(error)}",
            operation="task_error",
            task_name=task_name,
            task_id=task_id,
            error_category=ErrorCategory.CELERY,
            alert_level="medium",
            **kwargs
        )
    
    def log_external_api_call(self, service: str, endpoint: str, 
                             status_code: int, duration: float, **kwargs):
        """Log external API call."""
        level = logging.WARNING if status_code >= 400 else logging.INFO
        self._log_with_context(
            level,
            f"External API call: {service} {endpoint} - {status_code}",
            operation="external_api_call",
            service=service,
            endpoint=endpoint,
            status_code=status_code,
            duration=duration,
            **kwargs
        )
    
    def log_database_operation(self, operation: str, table: str, 
                              duration: float, **kwargs):
        """Log database operation."""
        self.debug(
            f"Database {operation}: {table}",
            operation="database_operation",
            db_operation=operation,
            table=table,
            duration=duration,
            **kwargs
        )


def set_request_context(request_id: str = None, user_id: int = None):
    """Set request context for correlation logging."""
    if request_id is None:
        request_id = str(uuid.uuid4())
    
    request_id_var.set(request_id)
    if user_id:
        user_id_var.set(user_id)
    
    return request_id


def clear_request_context():
    """Clear request context."""
    request_id_var.set(None)
    user_id_var.set(None)


def get_request_id() -> Optional[str]:
    """Get current request ID."""
    return request_id_var.get()


def setup_logging() -> None:
    """Setup application logging configuration."""
    
    # Determine log level
    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
    
    # Configure logging based on format preference
    if settings.LOG_FORMAT.lower() == "json":
        # JSON structured logging
        logging_config = {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "json": {
                    "()": JSONFormatter,
                },
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "formatter": "json",
                    "stream": sys.stdout,
                },
            },
            "root": {
                "level": log_level,
                "handlers": ["console"],
            },
            "loggers": {
                "app": {
                    "level": log_level,
                    "handlers": ["console"],
                    "propagate": False,
                },
                "uvicorn": {
                    "level": log_level,
                    "handlers": ["console"],
                    "propagate": False,
                },
                "celery": {
                    "level": log_level,
                    "handlers": ["console"],
                    "propagate": False,
                },
            },
        }
    else:
        # Standard text logging
        logging_config = {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "standard": {
                    "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
                    "datefmt": "%Y-%m-%d %H:%M:%S",
                },
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "formatter": "standard",
                    "stream": sys.stdout,
                },
            },
            "root": {
                "level": log_level,
                "handlers": ["console"],
            },
            "loggers": {
                "app": {
                    "level": log_level,
                    "handlers": ["console"],
                    "propagate": False,
                },
                "uvicorn": {
                    "level": log_level,
                    "handlers": ["console"],
                    "propagate": False,
                },
                "celery": {
                    "level": log_level,
                    "handlers": ["console"],
                    "propagate": False,
                },
            },
        }
    
    logging.config.dictConfig(logging_config)


class LogFilter:
    """Custom log filter for advanced filtering."""
    
    def __init__(self, min_level: str = None, max_level: str = None, 
                 categories: List[str] = None, exclude_categories: List[str] = None):
        self.min_level = getattr(logging, min_level.upper()) if min_level else 0
        self.max_level = getattr(logging, max_level.upper()) if max_level else 100
        self.categories = categories or []
        self.exclude_categories = exclude_categories or []
    
    def filter(self, record: logging.LogRecord) -> bool:
        """Filter log records based on criteria."""
        # Level filtering
        if not (self.min_level <= record.levelno <= self.max_level):
            return False
        
        # Category filtering
        error_category = getattr(record, 'error_category', None)
        if error_category:
            if self.categories and error_category not in self.categories:
                return False
            if self.exclude_categories and error_category in self.exclude_categories:
                return False
        
        return True


class AlertHandler(logging.Handler):
    """Custom handler for error alerting."""
    
    def __init__(self):
        super().__init__()
        self.setLevel(logging.ERROR)
    
    def emit(self, record: logging.LogRecord):
        """Send alert for critical errors."""
        try:
            # Only alert for high priority errors
            alert_level = getattr(record, 'alert_level', 'low')
            if alert_level in ['high', 'critical']:
                self._send_alert(record)
        except Exception:
            # Don't let alerting failures break the application
            pass
    
    def _send_alert(self, record: logging.LogRecord):
        """Send alert notification."""
        # Prepare alert data
        alert_data = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "error_category": getattr(record, 'error_category', 'unknown'),
            "alert_level": getattr(record, 'alert_level', 'unknown'),
            "request_id": getattr(record, 'request_id', None),
            "user_id": getattr(record, 'user_id', None),
        }
        
        # Add exception info if available
        if record.exc_info:
            alert_data["exception"] = {
                "type": record.exc_info[0].__name__ if record.exc_info[0] else None,
                "message": str(record.exc_info[1]) if record.exc_info[1] else None
            }
        
        # In development, just print to stderr
        if settings.ENVIRONMENT != "production":
            print(f"ALERT: {json.dumps(alert_data)}", file=sys.stderr)
            return
        
        # In production, send to alert notifier
        # We use asyncio.create_task to avoid blocking the logging thread
        # This is not ideal for synchronous code, but it's a compromise
        try:
            # Import here to avoid circular imports
            from app.core.alert_notifier import send_alert
            
            # Create a background task to send the alert
            loop = asyncio.get_event_loop()
            if loop.is_running():
                asyncio.create_task(
                    send_alert(
                        message=record.getMessage(),
                        error_category=getattr(record, 'error_category', 'unknown'),
                        alert_level=getattr(record, 'alert_level', 'unknown'),
                        details=alert_data
                    )
                )
            else:
                # If no event loop is running, just print to stderr
                print(f"ALERT: {json.dumps(alert_data)}", file=sys.stderr)
        except Exception as e:
            # If anything goes wrong, fall back to stderr
            print(f"ALERT: {json.dumps(alert_data)}", file=sys.stderr)
            print(f"Error sending alert: {str(e)}", file=sys.stderr)


def configure_advanced_logging():
    """Configure advanced logging features."""
    # Add alert handler for critical errors
    alert_handler = AlertHandler()
    logging.getLogger().addHandler(alert_handler)
    
    # Configure specific loggers with filters
    if settings.ENVIRONMENT == "production":
        # In production, filter out debug logs from external libraries
        external_filter = LogFilter(min_level="INFO")
        for logger_name in ["urllib3", "requests", "httpx"]:
            logger = logging.getLogger(logger_name)
            logger.addFilter(external_filter)


def get_logger(name: str) -> StructuredLogger:
    """Get enhanced logger instance with structured logging capabilities."""
    return StructuredLogger(name)


def get_standard_logger(name: str) -> logging.Logger:
    """Get standard logger instance for backward compatibility."""
    return logging.getLogger(name)


def log_function_call(func_name: str = None):
    """
    Decorator to automatically log function calls with parameters and execution time.
    
    Args:
        func_name: Optional custom function name for logging
    """
    def decorator(func):
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            logger = get_logger(func.__module__)
            name = func_name or func.__name__
            
            # Filter sensitive parameters
            safe_kwargs = {k: v for k, v in kwargs.items() 
                          if k not in ['password', 'token', 'secret', 'key']}
            
            start_time = time.time()
            logger.debug(
                f"Function call started: {name}",
                operation="function_call_start",
                function=name,
                args_count=len(args),
                kwargs=safe_kwargs
            )
            
            try:
                result = await func(*args, **kwargs)
                duration = (time.time() - start_time) * 1000
                
                logger.debug(
                    f"Function call completed: {name}",
                    operation="function_call_complete",
                    function=name,
                    duration=duration,
                    result_type=type(result).__name__ if result is not None else "None"
                )
                
                return result
            except Exception as e:
                duration = (time.time() - start_time) * 1000
                
                logger.error(
                    f"Function call failed: {name}",
                    operation="function_call_error",
                    function=name,
                    duration=duration,
                    error=str(e),
                    exc_info=True
                )
                raise
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            logger = get_logger(func.__module__)
            name = func_name or func.__name__
            
            # Filter sensitive parameters
            safe_kwargs = {k: v for k, v in kwargs.items() 
                          if k not in ['password', 'token', 'secret', 'key']}
            
            start_time = time.time()
            logger.debug(
                f"Function call started: {name}",
                operation="function_call_start",
                function=name,
                args_count=len(args),
                kwargs=safe_kwargs
            )
            
            try:
                result = func(*args, **kwargs)
                duration = (time.time() - start_time) * 1000
                
                logger.debug(
                    f"Function call completed: {name}",
                    operation="function_call_complete",
                    function=name,
                    duration=duration,
                    result_type=type(result).__name__ if result is not None else "None"
                )
                
                return result
            except Exception as e:
                duration = (time.time() - start_time) * 1000
                
                logger.error(
                    f"Function call failed: {name}",
                    operation="function_call_error",
                    function=name,
                    duration=duration,
                    error=str(e),
                    exc_info=True
                )
                raise
        
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper
    
    return decorator


def log_business_event(event_type: str, **kwargs):
    """
    Log business events for analytics and monitoring.
    
    Args:
        event_type: Type of business event (e.g., "user_registered", "content_generated")
        **kwargs: Additional event data
    """
    logger = get_logger("business_events")
    
    # Filter sensitive data
    safe_kwargs = {k: v for k, v in kwargs.items() 
                  if k not in ['password', 'token', 'secret', 'key']}
    
    logger.info(
        f"Business event: {event_type}",
        operation="business_event",
        event_type=event_type,
        **safe_kwargs
    )


def log_security_event(event_type: str, severity: str = "medium", **kwargs):
    """
    Log security-related events for monitoring and alerting.
    
    Args:
        event_type: Type of security event (e.g., "failed_login", "unauthorized_access")
        severity: Severity level (low, medium, high, critical)
        **kwargs: Additional event data
    """
    logger = get_logger("security_events")
    
    # Filter sensitive data but keep relevant security info
    safe_kwargs = {k: v for k, v in kwargs.items() 
                  if k not in ['password', 'token', 'secret']}
    
    # Determine log level based on severity
    if severity in ["high", "critical"]:
        log_level = logging.ERROR
        alert_level = severity
    elif severity == "medium":
        log_level = logging.WARNING
        alert_level = "medium"
    else:
        log_level = logging.INFO
        alert_level = "low"
    
    logger._log_with_context(
        log_level,
        f"Security event: {event_type}",
        operation="security_event",
        event_type=event_type,
        severity=severity,
        error_category=ErrorCategory.AUTHENTICATION,
        alert_level=alert_level,
        **safe_kwargs
    )


def log_performance_metric(metric_name: str, value: float, unit: str = "ms", **kwargs):
    """
    Log performance metrics for monitoring.
    
    Args:
        metric_name: Name of the metric (e.g., "api_response_time", "db_query_time")
        value: Metric value
        unit: Unit of measurement (ms, seconds, bytes, etc.)
        **kwargs: Additional metric data
    """
    logger = get_logger("performance_metrics")
    
    logger.info(
        f"Performance metric: {metric_name} = {value}{unit}",
        operation="performance_metric",
        metric_name=metric_name,
        metric_value=value,
        metric_unit=unit,
        **kwargs
    )


def truncate_string(value: str, max_length: int = None) -> str:
    """
    Truncate string for logging to prevent excessive log sizes.
    
    Args:
        value: String to truncate
        max_length: Maximum length (defaults to LOG_MAX_STRING_LENGTH from settings)
    
    Returns:
        Truncated string
    """
    if max_length is None:
        max_length = settings.LOG_MAX_STRING_LENGTH
    
    if len(value) <= max_length:
        return value
    
    return value[:max_length] + "... [truncated]"


def sanitize_log_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Sanitize log data by removing sensitive information and truncating long strings.
    
    Args:
        data: Dictionary of log data
    
    Returns:
        Sanitized dictionary
    """
    sensitive_keys = {'password', 'token', 'secret', 'key', 'auth', 'credential'}
    sanitized = {}
    
    for key, value in data.items():
        # Skip sensitive keys
        if any(sensitive_key in key.lower() for sensitive_key in sensitive_keys):
            sanitized[key] = "[REDACTED]"
            continue
        
        # Truncate long strings
        if isinstance(value, str):
            sanitized[key] = truncate_string(value)
        elif isinstance(value, dict):
            sanitized[key] = sanitize_log_data(value)
        elif isinstance(value, list) and len(value) > 10:
            # Truncate long lists
            sanitized[key] = value[:10] + ["... [truncated]"]
        else:
            sanitized[key] = value
    
    return sanitized