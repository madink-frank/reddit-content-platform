#!/usr/bin/env python3
"""
Demo script to test the structured logging system.
"""

import asyncio
import sys
import os

# Add the app directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.core.logging import (
    setup_logging, 
    configure_advanced_logging, 
    get_logger, 
    set_request_context, 
    clear_request_context,
    ErrorCategory
)


async def demo_logging():
    """Demonstrate the structured logging system."""
    
    # Setup logging
    setup_logging()
    configure_advanced_logging()
    
    # Get logger
    logger = get_logger(__name__)
    
    print("=== Structured Logging Demo ===\n")
    
    # Basic logging
    logger.info("Application started", operation="app_startup")
    logger.debug("Debug message with details", operation="debug_test", user_id=123)
    
    # Request context logging
    set_request_context(request_id="demo-request-123", user_id=456)
    logger.info("Processing request with context", operation="request_processing")
    
    # Error logging with categorization
    logger.error(
        "Database connection failed", 
        error_category=ErrorCategory.DATABASE,
        alert_level="high",
        operation="db_connection",
        connection_string="postgresql://localhost:5432/demo"
    )
    
    # External API logging
    logger.log_external_api_call(
        service="reddit",
        endpoint="/api/posts",
        status_code=200,
        duration=150.5,
        response_size=1024
    )
    
    # Task logging
    logger.log_task_start(
        task_name="crawl_reddit_posts",
        task_id="task-123",
        keyword="python"
    )
    
    logger.log_task_complete(
        task_name="crawl_reddit_posts",
        task_id="task-123",
        duration=30.2,
        posts_collected=25
    )
    
    # Exception logging
    try:
        raise ValueError("Demo exception for testing")
    except ValueError as e:
        logger.error(
            "Exception occurred during processing",
            error_category=ErrorCategory.VALIDATION,
            alert_level="medium",
            operation="data_validation",
            exc_info=True
        )
    
    # Critical error (should trigger alert)
    logger.critical(
        "System is running out of memory",
        error_category=ErrorCategory.SYSTEM,
        alert_level="critical",
        operation="system_monitoring",
        memory_usage_percent=95
    )
    
    # Clear context
    clear_request_context()
    
    logger.info("Demo completed", operation="demo_complete")
    
    print("\n=== Demo Complete ===")
    print("Check the logs above to see structured JSON output")


if __name__ == "__main__":
    asyncio.run(demo_logging())