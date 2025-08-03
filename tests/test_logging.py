"""
Tests for the structured logging system.
"""

import json
import logging
import pytest
from unittest.mock import patch, MagicMock
from fastapi import FastAPI
from fastapi.testclient import TestClient
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.logging import (
    JSONFormatter, 
    StructuredLogger, 
    set_request_context, 
    clear_request_context, 
    get_request_id,
    ErrorCategory,
    LogFilter,
    AlertHandler
)
from app.core.middleware import RequestTrackingMiddleware, LoggingMiddleware, ErrorHandlingMiddleware


class TestJSONFormatter:
    """Test the JSON formatter for structured logging."""
    
    def test_format_basic_record(self):
        """Test formatting a basic log record."""
        formatter = JSONFormatter()
        record = logging.LogRecord(
            name="test_logger",
            level=logging.INFO,
            pathname="test_file.py",
            lineno=42,
            msg="Test message",
            args=(),
            exc_info=None
        )
        
        result = formatter.format(record)
        log_entry = json.loads(result)
        
        assert log_entry["level"] == "INFO"
        assert log_entry["logger"] == "test_logger"
        assert log_entry["message"] == "Test message"
        assert log_entry["line"] == 42
        assert "timestamp" in log_entry
        assert "environment" in log_entry
        assert "service" in log_entry
        assert "version" in log_entry
    
    def test_format_with_exception(self):
        """Test formatting a log record with exception info."""
        formatter = JSONFormatter()
        try:
            raise ValueError("Test exception")
        except ValueError:
            import sys
            record = logging.LogRecord(
                name="test_logger",
                level=logging.ERROR,
                pathname="test_file.py",
                lineno=42,
                msg="Error occurred",
                args=(),
                exc_info=sys.exc_info()
            )
            
            result = formatter.format(record)
            log_entry = json.loads(result)
            
            assert log_entry["level"] == "ERROR"
            assert "exception" in log_entry
            assert log_entry["exception"]["type"] == "ValueError"
            assert log_entry["exception"]["message"] == "Test exception"
            assert "traceback" in log_entry["exception"]
    
    def test_format_with_custom_fields(self):
        """Test formatting a log record with custom fields."""
        formatter = JSONFormatter()
        record = logging.LogRecord(
            name="test_logger",
            level=logging.INFO,
            pathname="test_file.py",
            lineno=42,
            msg="Test message",
            args=(),
            exc_info=None
        )
        
        # Add custom fields
        record.request_id = "test-request-id"
        record.user_id = 123
        record.operation = "test_operation"
        record.duration = 0.5
        record.status_code = 200
        record.error_category = "validation"
        record.alert_level = "low"
        
        result = formatter.format(record)
        log_entry = json.loads(result)
        
        assert log_entry["request_id"] == "test-request-id"
        assert log_entry["user_id"] == 123
        assert log_entry["operation"] == "test_operation"
        assert log_entry["duration"] == 0.5
        assert log_entry["status_code"] == 200
        assert log_entry["error_category"] == "validation"
        assert log_entry["alert_level"] == "low"


class TestStructuredLogger:
    """Test the structured logger functionality."""
    
    @pytest.fixture
    def logger(self):
        """Create a test structured logger."""
        return StructuredLogger("test_structured_logger")
    
    def test_debug_log(self, logger, caplog):
        """Test debug level logging."""
        with caplog.at_level(logging.DEBUG):
            logger.debug("Debug message", operation="test_debug")
            assert "Debug message" in caplog.text
    
    def test_info_log(self, logger, caplog):
        """Test info level logging."""
        with caplog.at_level(logging.INFO):
            logger.info("Info message", operation="test_info")
            assert "Info message" in caplog.text
    
    def test_warning_log(self, logger, caplog):
        """Test warning level logging."""
        with caplog.at_level(logging.WARNING):
            logger.warning("Warning message", operation="test_warning")
            assert "Warning message" in caplog.text
    
    def test_error_log(self, logger, caplog):
        """Test error level logging with categorization."""
        with caplog.at_level(logging.ERROR):
            logger.error(
                "Error message", 
                error_category=ErrorCategory.VALIDATION, 
                alert_level="medium",
                operation="test_error"
            )
            assert "Error message" in caplog.text
            
            # Check if the record has the correct attributes
            for record in caplog.records:
                if record.message == "Error message":
                    assert record.error_category == "validation"
                    assert record.alert_level == "medium"
                    assert record.operation == "test_error"
    
    def test_critical_log(self, logger, caplog):
        """Test critical level logging with high alert."""
        with caplog.at_level(logging.CRITICAL):
            logger.critical(
                "Critical message", 
                error_category=ErrorCategory.DATABASE, 
                alert_level="high",
                operation="test_critical"
            )
            assert "Critical message" in caplog.text
            
            # Check if the record has the correct attributes
            for record in caplog.records:
                if record.message == "Critical message":
                    assert record.error_category == "database"
                    assert record.alert_level == "high"
                    assert record.operation == "test_critical"
    
    def test_log_request(self, logger, caplog):
        """Test request logging."""
        with caplog.at_level(logging.INFO):
            logger.log_request(
                method="GET",
                path="/api/test",
                status_code=200,
                duration=0.1,
                query_params={"q": "test"},
                user_agent="Test User Agent"
            )
            
            assert "GET /api/test - 200" in caplog.text
            
            # Check if the record has the correct attributes
            for record in caplog.records:
                if "GET /api/test - 200" in record.message:
                    assert record.operation == "http_request"
                    assert record.method == "GET"
                    assert record.path == "/api/test"
                    assert record.status_code == 200
                    assert record.duration == 0.1
                    assert record.query_params == {"q": "test"}
                    assert record.user_agent == "Test User Agent"
    
    def test_log_external_api_call(self, logger, caplog):
        """Test external API call logging."""
        with caplog.at_level(logging.INFO):
            # Successful API call (2xx)
            logger.log_external_api_call(
                service="reddit",
                endpoint="/api/posts",
                status_code=200,
                duration=0.3
            )
            
            assert "External API call: reddit /api/posts - 200" in caplog.text
        
        with caplog.at_level(logging.WARNING):
            # Failed API call (4xx)
            logger.log_external_api_call(
                service="reddit",
                endpoint="/api/posts",
                status_code=429,
                duration=0.2,
                error="Rate limited"
            )
            
            assert "External API call: reddit /api/posts - 429" in caplog.text
            
            # Check if the record has the correct attributes
            for record in caplog.records:
                if "External API call: reddit /api/posts - 429" in record.message:
                    assert record.operation == "external_api_call"
                    assert record.service == "reddit"
                    assert record.endpoint == "/api/posts"
                    assert record.status_code == 429
                    assert record.duration == 0.2
                    assert record.error == "Rate limited"


class TestRequestContext:
    """Test request context management."""
    
    def test_set_and_get_request_id(self):
        """Test setting and getting request ID."""
        # Clear any existing context
        clear_request_context()
        
        # Set request context
        request_id = set_request_context(request_id="test-request-id", user_id=123)
        
        # Get request ID
        assert get_request_id() == "test-request-id"
        assert request_id == "test-request-id"
        
        # Clear context
        clear_request_context()
        assert get_request_id() is None
    
    def test_auto_generate_request_id(self):
        """Test auto-generation of request ID."""
        # Clear any existing context
        clear_request_context()
        
        # Set request context without explicit request ID
        request_id = set_request_context(user_id=123)
        
        # Verify request ID was generated
        assert request_id is not None
        assert get_request_id() == request_id
        
        # Clear context
        clear_request_context()


class TestLogFilter:
    """Test log filtering functionality."""
    
    def test_level_filtering(self):
        """Test filtering by log level."""
        # Filter logs between INFO and ERROR
        log_filter = LogFilter(min_level="INFO", max_level="ERROR")
        
        # Create test records
        debug_record = logging.LogRecord(
            name="test", level=logging.DEBUG, pathname="", lineno=0,
            msg="Debug message", args=(), exc_info=None
        )
        
        info_record = logging.LogRecord(
            name="test", level=logging.INFO, pathname="", lineno=0,
            msg="Info message", args=(), exc_info=None
        )
        
        error_record = logging.LogRecord(
            name="test", level=logging.ERROR, pathname="", lineno=0,
            msg="Error message", args=(), exc_info=None
        )
        
        critical_record = logging.LogRecord(
            name="test", level=logging.CRITICAL, pathname="", lineno=0,
            msg="Critical message", args=(), exc_info=None
        )
        
        # Test filtering
        assert not log_filter.filter(debug_record)  # Below min_level
        assert log_filter.filter(info_record)       # Within range
        assert log_filter.filter(error_record)      # Within range
        assert not log_filter.filter(critical_record)  # Above max_level
    
    def test_category_filtering(self):
        """Test filtering by error category."""
        # Filter logs with database or validation categories
        log_filter = LogFilter(categories=["database", "validation"])
        
        # Create test records with categories
        db_record = logging.LogRecord(
            name="test", level=logging.ERROR, pathname="", lineno=0,
            msg="Database error", args=(), exc_info=None
        )
        db_record.error_category = "database"
        
        auth_record = logging.LogRecord(
            name="test", level=logging.ERROR, pathname="", lineno=0,
            msg="Auth error", args=(), exc_info=None
        )
        auth_record.error_category = "authentication"
        
        # Test filtering
        assert log_filter.filter(db_record)      # Included category
        assert not log_filter.filter(auth_record)  # Excluded category
    
    def test_exclude_category_filtering(self):
        """Test filtering by excluded categories."""
        # Filter logs excluding system and database categories
        log_filter = LogFilter(exclude_categories=["system", "database"])
        
        # Create test records with categories
        db_record = logging.LogRecord(
            name="test", level=logging.ERROR, pathname="", lineno=0,
            msg="Database error", args=(), exc_info=None
        )
        db_record.error_category = "database"
        
        auth_record = logging.LogRecord(
            name="test", level=logging.ERROR, pathname="", lineno=0,
            msg="Auth error", args=(), exc_info=None
        )
        auth_record.error_category = "authentication"
        
        # Test filtering
        assert not log_filter.filter(db_record)  # Excluded category
        assert log_filter.filter(auth_record)    # Not excluded category


class TestAlertHandler:
    """Test alert handler functionality."""
    
    @patch('builtins.print')
    def test_emit_high_alert(self, mock_print):
        """Test emitting high priority alerts."""
        handler = AlertHandler()
        
        # Create a high priority error record
        record = logging.LogRecord(
            name="test", level=logging.CRITICAL, pathname="", lineno=0,
            msg="Critical system error", args=(), exc_info=None
        )
        record.alert_level = "high"
        record.error_category = "system"
        record.request_id = "test-request-id"
        
        # Emit the alert
        handler.emit(record)
        
        # Verify alert was printed
        mock_print.assert_called_once()
        alert_arg = mock_print.call_args[0][0]
        assert "ALERT:" in alert_arg
        assert "Critical system error" in alert_arg
    
    @patch('builtins.print')
    def test_ignore_low_alert(self, mock_print):
        """Test that low priority alerts are ignored."""
        handler = AlertHandler()
        
        # Create a low priority error record
        record = logging.LogRecord(
            name="test", level=logging.ERROR, pathname="", lineno=0,
            msg="Minor error", args=(), exc_info=None
        )
        record.alert_level = "low"
        record.error_category = "validation"
        
        # Emit the alert
        handler.emit(record)
        
        # Verify no alert was printed
        mock_print.assert_not_called()


class TestRequestTrackingMiddleware:
    """Test request tracking middleware."""
    
    def test_request_tracking(self):
        """Test request tracking middleware adds request ID."""
        app = FastAPI()
        app.add_middleware(RequestTrackingMiddleware)
        
        @app.get("/test")
        async def test_endpoint():
            return {"request_id": get_request_id()}
        
        client = TestClient(app)
        response = client.get("/test")
        
        assert response.status_code == 200
        assert "request_id" in response.json()
        assert response.headers.get("X-Request-ID") is not None
        assert response.json()["request_id"] == response.headers.get("X-Request-ID")
    
    def test_custom_request_id(self):
        """Test middleware uses custom request ID from header."""
        app = FastAPI()
        app.add_middleware(RequestTrackingMiddleware)
        
        @app.get("/test")
        async def test_endpoint():
            return {"request_id": get_request_id()}
        
        client = TestClient(app)
        custom_id = "custom-request-id-123"
        response = client.get("/test", headers={"X-Request-ID": custom_id})
        
        assert response.status_code == 200
        assert response.json()["request_id"] == custom_id
        assert response.headers.get("X-Request-ID") == custom_id


class TestErrorHandlingMiddleware:
    """Test error handling middleware."""
    
    def test_validation_error_handling(self):
        """Test handling of validation errors."""
        app = FastAPI()
        app.add_middleware(ErrorHandlingMiddleware)
        
        @app.get("/validation-error")
        async def validation_error():
            raise ValueError("Invalid input")
        
        client = TestClient(app)
        response = client.get("/validation-error")
        
        assert response.status_code == 400
        assert response.json()["error"] == "Bad Request"
        assert response.json()["message"] == "Invalid input"
    
    def test_permission_error_handling(self):
        """Test handling of permission errors."""
        app = FastAPI()
        app.add_middleware(ErrorHandlingMiddleware)
        
        @app.get("/permission-error")
        async def permission_error():
            raise PermissionError("Access denied")
        
        client = TestClient(app)
        response = client.get("/permission-error")
        
        assert response.status_code == 403
        assert response.json()["error"] == "Forbidden"
        assert response.json()["message"] == "Access denied"
    
    def test_generic_error_handling(self):
        """Test handling of generic errors."""
        app = FastAPI()
        app.add_middleware(ErrorHandlingMiddleware)
        
        @app.get("/generic-error")
        async def generic_error():
            raise Exception("Something went wrong")
        
        client = TestClient(app)
        response = client.get("/generic-error")
        
        assert response.status_code == 500
        assert response.json()["error"] == "Internal Server Error"
        assert response.json()["message"] == "An unexpected error occurred"


class TestUtilityFunctions:
    """Test utility functions for logging."""
    
    def test_sanitize_log_data(self):
        """Test data sanitization function."""
        from app.core.logging import sanitize_log_data
        
        data = {
            "username": "testuser",
            "password": "secret123",
            "api_token": "abc123",
            "normal_field": "normal_value",
            "nested": {
                "secret_key": "hidden",
                "public_info": "visible"
            },
            "long_string": "x" * 2000,
            "long_list": list(range(20))
        }
        
        sanitized = sanitize_log_data(data)
        
        assert sanitized["username"] == "testuser"
        assert sanitized["password"] == "[REDACTED]"
        assert sanitized["api_token"] == "[REDACTED]"
        assert sanitized["normal_field"] == "normal_value"
        assert sanitized["nested"]["secret_key"] == "[REDACTED]"
        assert sanitized["nested"]["public_info"] == "visible"
        assert "... [truncated]" in sanitized["long_string"]
        assert "... [truncated]" in str(sanitized["long_list"])
    
    def test_truncate_string(self):
        """Test string truncation function."""
        from app.core.logging import truncate_string
        
        # Short string should not be truncated
        short_string = "short"
        assert truncate_string(short_string, 100) == "short"
        
        # Long string should be truncated
        long_string = "x" * 200
        truncated = truncate_string(long_string, 50)
        assert len(truncated) <= 65  # 50 + "... [truncated]"
        assert truncated.endswith("... [truncated]")
    
    def test_log_business_event(self, caplog):
        """Test business event logging."""
        from app.core.logging import log_business_event
        
        with caplog.at_level(logging.INFO):
            log_business_event(
                "user_registered",
                user_id=123,
                email="test@example.com"
            )
            
            assert "Business event: user_registered" in caplog.text
    
    def test_log_security_event(self, caplog):
        """Test security event logging."""
        from app.core.logging import log_security_event
        
        with caplog.at_level(logging.WARNING):
            log_security_event(
                "failed_login",
                severity="medium",
                user_id=456,
                ip_address="192.168.1.1"
            )
            
            assert "Security event: failed_login" in caplog.text
    
    def test_log_performance_metric(self, caplog):
        """Test performance metric logging."""
        from app.core.logging import log_performance_metric
        
        with caplog.at_level(logging.INFO):
            log_performance_metric(
                "api_response_time",
                value=150.5,
                unit="ms",
                endpoint="/api/test"
            )
            
            assert "Performance metric: api_response_time = 150.5ms" in caplog.text


class TestFunctionCallDecorator:
    """Test the function call logging decorator."""
    
    @pytest.mark.asyncio
    async def test_async_function_decorator(self, caplog):
        """Test decorator with async function."""
        from app.core.logging import log_function_call
        
        @log_function_call()
        async def test_async_func(param1: str, param2: int = 42):
            return f"result_{param1}_{param2}"
        
        with caplog.at_level(logging.DEBUG):
            result = await test_async_func("test", param2=100)
            
            assert result == "result_test_100"
            # Check that function calls were logged
            assert any("Function call started: test_async_func" in record.message 
                      for record in caplog.records)
            assert any("Function call completed: test_async_func" in record.message 
                      for record in caplog.records)
    
    def test_sync_function_decorator(self, caplog):
        """Test decorator with sync function."""
        from app.core.logging import log_function_call
        
        @log_function_call("custom_function_name")
        def test_sync_func(param1: str):
            return f"sync_{param1}"
        
        with caplog.at_level(logging.DEBUG):
            result = test_sync_func("test")
            
            assert result == "sync_test"
            # Check that function calls were logged with custom name
            assert any("Function call started: custom_function_name" in record.message 
                      for record in caplog.records)
            assert any("Function call completed: custom_function_name" in record.message 
                      for record in caplog.records)
    
    @pytest.mark.asyncio
    async def test_function_decorator_error_handling(self, caplog):
        """Test decorator error handling."""
        from app.core.logging import log_function_call
        
        @log_function_call()
        async def failing_function():
            raise ValueError("Test error")
        
        with caplog.at_level(logging.ERROR):
            with pytest.raises(ValueError):
                await failing_function()
            
            # Check that error was logged
            assert any("Function call failed: failing_function" in record.message 
                      for record in caplog.records)


if __name__ == "__main__":
    pytest.main(["-xvs", __file__])