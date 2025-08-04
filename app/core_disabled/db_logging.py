"""
SQLAlchemy query logging integration with structured logging.
"""

import time
import functools
from typing import Any, Callable, Dict, Optional, Type, TypeVar, cast

from sqlalchemy import event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session
from sqlalchemy.ext.declarative import DeclarativeMeta

from app.core.logging import get_logger, ErrorCategory
from app.core.config import settings


logger = get_logger(__name__)

# Type variable for function return type
T = TypeVar('T')


def log_slow_queries(threshold_ms: float = 100.0):
    """
    Log queries that exceed the specified threshold.
    
    Args:
        threshold_ms: Threshold in milliseconds for slow query detection
    """
    @event.listens_for(Engine, "before_cursor_execute")
    def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
        # Store execution start time in context
        context._query_start_time = time.time()
    
    @event.listens_for(Engine, "after_cursor_execute")
    def after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
        # Calculate query execution time
        duration = (time.time() - context._query_start_time) * 1000  # Convert to ms
        
        # Log slow queries
        if duration > threshold_ms:
            logger.warning(
                f"Slow query detected: {duration:.2f}ms",
                operation="slow_query",
                query=statement,
                parameters=str(parameters),
                duration=duration,
                threshold=threshold_ms
            )


def setup_query_logging():
    """Setup SQLAlchemy query logging if enabled in settings."""
    if settings.LOG_SQL_QUERIES:
        # Log all queries in debug mode
        @event.listens_for(Engine, "before_cursor_execute")
        def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
            context._query_start_time = time.time()
            
            if settings.LOG_LEVEL.upper() == "DEBUG":
                logger.debug(
                    "Executing SQL query",
                    operation="sql_query",
                    query=statement,
                    parameters=str(parameters),
                    executemany=executemany
                )
        
        @event.listens_for(Engine, "after_cursor_execute")
        def after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
            duration = (time.time() - context._query_start_time) * 1000  # Convert to ms
            
            # Log query execution time
            if settings.LOG_LEVEL.upper() == "DEBUG":
                logger.debug(
                    f"SQL query executed in {duration:.2f}ms",
                    operation="sql_query_completed",
                    duration=duration
                )
        
        # Setup slow query logging with configurable threshold
        log_slow_queries(threshold_ms=settings.SLOW_QUERY_THRESHOLD_MS if hasattr(settings, 'SLOW_QUERY_THRESHOLD_MS') else 100.0)


def log_db_operation(operation_type: str):
    """
    Decorator to log database operations with timing.
    
    Args:
        operation_type: Type of database operation (e.g., "create", "update", "delete")
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> T:
            # Extract model class name if available
            model_class = None
            for arg in args:
                if isinstance(arg, DeclarativeMeta):
                    model_class = arg.__name__
                    break
            
            # Get table name from first argument if it's a model instance
            table_name = None
            if args and hasattr(args[0], "__tablename__"):
                table_name = args[0].__tablename__
            elif model_class:
                table_name = model_class
            else:
                table_name = "unknown"
            
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                duration = (time.time() - start_time) * 1000  # Convert to ms
                
                # Log successful operation
                logger.debug(
                    f"Database {operation_type}: {table_name}",
                    operation="database_operation",
                    db_operation=operation_type,
                    table=table_name,
                    duration=duration
                )
                
                return result
            except Exception as e:
                duration = (time.time() - start_time) * 1000  # Convert to ms
                
                # Log failed operation
                logger.error(
                    f"Database {operation_type} failed: {table_name}",
                    error_category=ErrorCategory.DATABASE,
                    alert_level="medium" if operation_type in ["create", "update", "delete"] else "low",
                    operation="database_operation_failed",
                    db_operation=operation_type,
                    table=table_name,
                    duration=duration,
                    error=str(e),
                    exc_info=True
                )
                
                raise
        
        return wrapper
    
    return decorator


class LoggedSession(Session):
    """
    Extended SQLAlchemy Session with operation logging.
    """
    
    def add(self, instance, _warn=True):
        """Log add operation."""
        table_name = instance.__tablename__ if hasattr(instance, "__tablename__") else "unknown"
        start_time = time.time()
        
        try:
            result = super().add(instance, _warn=_warn)
            duration = (time.time() - start_time) * 1000
            
            logger.debug(
                f"Database add: {table_name}",
                operation="database_add",
                table=table_name,
                duration=duration
            )
            
            return result
        except Exception as e:
            duration = (time.time() - start_time) * 1000
            
            logger.error(
                f"Database add failed: {table_name}",
                error_category=ErrorCategory.DATABASE,
                alert_level="medium",
                operation="database_add_failed",
                table=table_name,
                duration=duration,
                error=str(e),
                exc_info=True
            )
            
            raise
    
    def delete(self, instance):
        """Log delete operation."""
        table_name = instance.__tablename__ if hasattr(instance, "__tablename__") else "unknown"
        start_time = time.time()
        
        try:
            result = super().delete(instance)
            duration = (time.time() - start_time) * 1000
            
            logger.debug(
                f"Database delete: {table_name}",
                operation="database_delete",
                table=table_name,
                duration=duration
            )
            
            return result
        except Exception as e:
            duration = (time.time() - start_time) * 1000
            
            logger.error(
                f"Database delete failed: {table_name}",
                error_category=ErrorCategory.DATABASE,
                alert_level="medium",
                operation="database_delete_failed",
                table=table_name,
                duration=duration,
                error=str(e),
                exc_info=True
            )
            
            raise
    
    def commit(self):
        """Log commit operation."""
        start_time = time.time()
        
        try:
            result = super().commit()
            duration = (time.time() - start_time) * 1000
            
            logger.debug(
                "Database commit",
                operation="database_commit",
                duration=duration
            )
            
            return result
        except Exception as e:
            duration = (time.time() - start_time) * 1000
            
            logger.error(
                "Database commit failed",
                error_category=ErrorCategory.DATABASE,
                alert_level="high",
                operation="database_commit_failed",
                duration=duration,
                error=str(e),
                exc_info=True
            )
            
            raise
    
    def rollback(self):
        """Log rollback operation."""
        start_time = time.time()
        
        try:
            result = super().rollback()
            duration = (time.time() - start_time) * 1000
            
            logger.debug(
                "Database rollback",
                operation="database_rollback",
                duration=duration
            )
            
            return result
        except Exception as e:
            duration = (time.time() - start_time) * 1000
            
            logger.error(
                "Database rollback failed",
                error_category=ErrorCategory.DATABASE,
                alert_level="high",
                operation="database_rollback_failed",
                duration=duration,
                error=str(e),
                exc_info=True
            )
            
            raise