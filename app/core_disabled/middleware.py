"""
Middleware for request tracking and logging.
"""

import time
import uuid
from typing import Callable
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from app.core.logging import get_logger, set_request_context, clear_request_context
from app.core.config import settings


logger = get_logger(__name__)


class RequestTrackingMiddleware(BaseHTTPMiddleware):
    """Middleware for tracking requests with correlation IDs."""
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request with tracking."""
        # Generate or extract request ID (support multiple header names)
        request_id = (
            request.headers.get("X-Request-ID") or 
            request.headers.get("X-Correlation-ID") or 
            request.headers.get(settings.LOG_CORRELATION_ID_HEADER) or
            str(uuid.uuid4())
        )
        
        # Extract user ID from request if available
        user_id = None
        if hasattr(request.state, "user") and request.state.user:
            user_id = request.state.user.id
        
        # Set request context
        set_request_context(request_id=request_id, user_id=user_id)
        
        # Add request ID to request state for access in endpoints
        request.state.request_id = request_id
        
        # Record start time
        start_time = time.time()
        
        # Check if path should be excluded from logging
        path = str(request.url.path)
        should_log = path not in settings.LOG_EXCLUDE_PATHS
        
        try:
            # Process request
            response = await call_next(request)
            
            # Calculate duration
            duration = (time.time() - start_time) * 1000  # Convert to ms
            
            # Log request (if not excluded)
            if should_log:
                logger.log_request(
                    method=request.method,
                    path=path,
                    status_code=response.status_code,
                    duration=duration,
                    query_params=dict(request.query_params) if request.query_params else None,
                    user_agent=request.headers.get("user-agent"),
                    client_ip=request.client.host if request.client else None,
                    content_length=response.headers.get("content-length")
                )
            
            # Add request ID to response headers
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Correlation-ID"] = request_id
            
            return response
            
        except Exception as exc:
            # Calculate duration for failed requests
            duration = (time.time() - start_time) * 1000
            
            # Log error (always log errors, even for excluded paths)
            logger.error(
                f"Request failed: {request.method} {path}",
                operation="request_error",
                method=request.method,
                path=path,
                duration=duration,
                error_message=str(exc),
                error_category=ErrorCategory.SYSTEM,
                alert_level="medium",
                exc_info=True
            )
            
            # Return error response
            return JSONResponse(
                status_code=500,
                content={
                    "error": "Internal Server Error",
                    "request_id": request_id,
                    "message": "An unexpected error occurred"
                },
                headers={
                    "X-Request-ID": request_id,
                    "X-Correlation-ID": request_id
                }
            )
        
        finally:
            # Clear request context
            clear_request_context()


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for detailed request/response logging."""
    
    def __init__(self, app: ASGIApp, log_requests: bool = True, log_responses: bool = False):
        super().__init__(app)
        self.log_requests = log_requests
        self.log_responses = log_responses
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Log request and response details."""
        if self.log_requests:
            # Log incoming request
            logger.debug(
                f"Incoming request: {request.method} {request.url}",
                operation="request_received",
                method=request.method,
                url=str(request.url),
                headers=dict(request.headers),
                client_ip=request.client.host if request.client else None
            )
        
        # Process request
        response = await call_next(request)
        
        if self.log_responses:
            # Log outgoing response
            logger.debug(
                f"Outgoing response: {response.status_code}",
                operation="response_sent",
                status_code=response.status_code,
                headers=dict(response.headers)
            )
        
        return response


class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    """Middleware for centralized error handling and logging."""
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Handle and log errors consistently."""
        try:
            return await call_next(request)
        
        except ValueError as exc:
            logger.error(
                f"Validation error: {str(exc)}",
                error_category="validation",
                alert_level="low",
                path=str(request.url.path),
                method=request.method
            )
            return JSONResponse(
                status_code=400,
                content={
                    "error": "Bad Request",
                    "message": str(exc),
                    "request_id": getattr(request.state, "request_id", None)
                }
            )
        
        except PermissionError as exc:
            logger.error(
                f"Permission denied: {str(exc)}",
                error_category="authorization",
                alert_level="medium",
                path=str(request.url.path),
                method=request.method
            )
            return JSONResponse(
                status_code=403,
                content={
                    "error": "Forbidden",
                    "message": "Access denied",
                    "request_id": getattr(request.state, "request_id", None)
                }
            )
        
        except Exception as exc:
            logger.critical(
                f"Unhandled exception: {str(exc)}",
                error_category="system",
                alert_level="high",
                path=str(request.url.path),
                method=request.method,
                exc_info=True
            )
            return JSONResponse(
                status_code=500,
                content={
                    "error": "Internal Server Error",
                    "message": "An unexpected error occurred",
                    "request_id": getattr(request.state, "request_id", None)
                }
            )