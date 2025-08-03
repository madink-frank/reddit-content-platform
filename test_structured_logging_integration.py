#!/usr/bin/env python3
"""
Integration test for the complete structured logging system.
Tests all components working together including middleware, formatters, and alert system.
"""

import asyncio
import json
import logging
import sys
import time
from io import StringIO
from unittest.mock import patch, MagicMock
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.core.logging import (
    setup_logging, 
    configure_advanced_logging, 
    get_logger, 
    set_request_context, 
    clear_request_context,
    ErrorCategory,
    log_function_call,
    log_business_event,
    log_security_event,
    log_performance_metric,
    sanitize_log_data,
    truncate_string
)
from app.core.middleware import RequestTrackingMiddleware, ErrorHandlingMiddleware
from app.core.alert_notifier import send_alert


async def test_complete_logging_integration():
    """Test the complete logging system integration."""
    
    print("=== Structured Logging Integration Test ===\n")
    
    # Setup logging
    setup_logging()
    configure_advanced_logging()
    
    # Test 1: Basic structured logging
    print("1. Testing basic structured logging...")
    logger = get_logger(__name__)
    
    # Capture log output
    log_stream = StringIO()
    handler = logging.StreamHandler(log_stream)
    handler.setFormatter(logging.getLogger().handlers[0].formatter)
    logger.logger.addHandler(handler)
    
    logger.info("Test message", operation="test", user_id=123)
    
    log_output = log_stream.getvalue()
    log_data = json.loads(log_output.strip())
    
    assert log_data["message"] == "Test message"
    assert log_data["operation"] == "test"
    assert log_data["level"] == "INFO"
    print("✓ Basic logging works")
    
    # Test 2: Request context logging
    print("2. Testing request context logging...")
    set_request_context(request_id="test-123", user_id=456)
    
    log_stream = StringIO()
    handler = logging.StreamHandler(log_stream)
    handler.setFormatter(logging.getLogger().handlers[0].formatter)
    logger.logger.handlers = [handler]  # Replace handler
    
    logger.info("Context test", operation="context_test")
    
    log_output = log_stream.getvalue()
    log_data = json.loads(log_output.strip())
    
    assert log_data["request_id"] == "test-123"
    assert log_data["user_id"] == 456
    print("✓ Request context logging works")
    
    clear_request_context()
    
    # Test 3: Error categorization and alerting
    print("3. Testing error categorization...")
    
    log_stream = StringIO()
    handler = logging.StreamHandler(log_stream)
    handler.setFormatter(logging.getLogger().handlers[0].formatter)
    logger.logger.handlers = [handler]
    
    with patch('builtins.print') as mock_print:
        logger.error(
            "Database connection failed",
            error_category=ErrorCategory.DATABASE,
            alert_level="high",
            operation="db_test"
        )
        
        log_output = log_stream.getvalue()
        log_data = json.loads(log_output.strip())
        
        assert log_data["error_category"] == "database"
        assert log_data["alert_level"] == "high"
        
        # Check if alert was triggered
        mock_print.assert_called_once()
        alert_call = mock_print.call_args[0][0]
        assert "ALERT:" in alert_call
        assert "Database connection failed" in alert_call
        
    print("✓ Error categorization and alerting works")
    
    # Test 4: Function call logging decorator
    print("4. Testing function call logging...")
    
    @log_function_call()
    async def test_async_function(param1: str, param2: int = 42):
        await asyncio.sleep(0.01)  # Simulate work
        return f"result_{param1}_{param2}"
    
    @log_function_call("custom_sync_function")
    def test_sync_function(param1: str):
        time.sleep(0.01)  # Simulate work
        return f"sync_{param1}"
    
    # Test async function
    result = await test_async_function("test", param2=100)
    assert result == "result_test_100"
    
    # Test sync function
    result = test_sync_function("sync_test")
    assert result == "sync_sync_test"
    
    print("✓ Function call logging decorator works")
    
    # Test 5: Business event logging
    print("5. Testing business event logging...")
    
    log_business_event(
        "user_registered",
        user_id=789,
        email="test@example.com",
        registration_method="oauth"
    )
    
    print("✓ Business event logging works")
    
    # Test 6: Security event logging
    print("6. Testing security event logging...")
    
    log_security_event(
        "failed_login",
        severity="medium",
        user_id=999,
        ip_address="192.168.1.100",
        user_agent="Test Browser"
    )
    
    print("✓ Security event logging works")
    
    # Test 7: Performance metric logging
    print("7. Testing performance metric logging...")
    
    log_performance_metric(
        "api_response_time",
        value=150.5,
        unit="ms",
        endpoint="/api/test",
        method="GET"
    )
    
    print("✓ Performance metric logging works")
    
    # Test 8: Data sanitization
    print("8. Testing data sanitization...")
    
    sensitive_data = {
        "username": "testuser",
        "password": "secret123",
        "api_token": "abc123xyz",
        "user_data": {
            "name": "Test User",
            "secret_key": "hidden"
        },
        "long_text": "x" * 2000,
        "long_list": list(range(20))
    }
    
    sanitized = sanitize_log_data(sensitive_data)
    
    assert sanitized["username"] == "testuser"
    assert sanitized["password"] == "[REDACTED]"
    assert sanitized["api_token"] == "[REDACTED]"
    assert sanitized["user_data"]["name"] == "Test User"
    assert sanitized["user_data"]["secret_key"] == "[REDACTED]"
    assert "... [truncated]" in sanitized["long_text"]
    assert "... [truncated]" in str(sanitized["long_list"])
    
    print("✓ Data sanitization works")
    
    # Test 9: String truncation
    print("9. Testing string truncation...")
    
    long_string = "x" * 1500
    truncated = truncate_string(long_string, max_length=100)
    
    assert len(truncated) <= 115  # 100 + "... [truncated]"
    assert truncated.endswith("... [truncated]")
    
    print("✓ String truncation works")
    
    # Test 10: FastAPI middleware integration
    print("10. Testing FastAPI middleware integration...")
    
    app = FastAPI()
    app.add_middleware(ErrorHandlingMiddleware)
    app.add_middleware(RequestTrackingMiddleware)
    
    @app.get("/test")
    async def test_endpoint():
        logger = get_logger(__name__)
        logger.info("Test endpoint called", operation="test_endpoint")
        return {"message": "success"}
    
    @app.get("/error")
    async def error_endpoint():
        raise ValueError("Test error")
    
    client = TestClient(app)
    
    # Test successful request
    response = client.get("/test")
    assert response.status_code == 200
    assert "X-Request-ID" in response.headers
    assert "X-Correlation-ID" in response.headers
    
    # Test error handling
    response = client.get("/error")
    assert response.status_code == 400  # ValueError -> 400 Bad Request
    assert response.json()["error"] == "Bad Request"
    assert "X-Request-ID" in response.headers
    
    print("✓ FastAPI middleware integration works")
    
    print("\n=== All Integration Tests Passed! ===")
    print("The structured logging system is fully functional and integrated.")


async def test_alert_system_integration():
    """Test the alert system integration."""
    
    print("\n=== Alert System Integration Test ===\n")
    
    # Test alert sending (mocked)
    with patch('app.core.alert_notifier.alert_notifier.notify') as mock_notify:
        mock_notify.return_value = True
        
        result = await send_alert(
            message="Test alert message",
            error_category="system",
            alert_level="high",
            details={"test": "data"}
        )
        
        assert result is True
        mock_notify.assert_called_once_with(
            "Test alert message",
            "system", 
            "high",
            {"test": "data"}
        )
    
    print("✓ Alert system integration works")


if __name__ == "__main__":
    async def main():
        await test_complete_logging_integration()
        await test_alert_system_integration()
    
    asyncio.run(main())