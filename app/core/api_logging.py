"""
External API call logging utilities.
"""

import time
import functools
import json
import asyncio
from typing import Any, Callable, Dict, Optional, TypeVar, cast
import httpx

from app.core.logging import get_logger, ErrorCategory


logger = get_logger(__name__)

# Type variable for function return type
T = TypeVar('T')


def log_api_call(service_name: str, endpoint: str = None):
    """
    Decorator to log external API calls with timing and status.
    
    Args:
        service_name: Name of the external service (e.g., "reddit", "github")
        endpoint: API endpoint being called (optional, can be extracted from URL)
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs) -> T:
            # Extract endpoint from URL if not provided
            nonlocal endpoint
            actual_endpoint = endpoint
            
            # Try to extract endpoint from URL in kwargs
            if not actual_endpoint:
                for param_name in ['url', 'endpoint', 'path']:
                    if param_name in kwargs:
                        url_value = kwargs[param_name]
                        if isinstance(url_value, str):
                            actual_endpoint = url_value.split('?')[0]  # Remove query params
                            break
            
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                duration = (time.time() - start_time) * 1000  # Convert to ms
                
                # Extract status code from response if available
                status_code = None
                if isinstance(result, httpx.Response):
                    status_code = result.status_code
                elif hasattr(result, 'status_code'):
                    status_code = result.status_code
                elif isinstance(result, dict) and 'status_code' in result:
                    status_code = result['status_code']
                
                # Log successful API call
                logger.log_external_api_call(
                    service=service_name,
                    endpoint=actual_endpoint or "unknown",
                    status_code=status_code or 200,
                    duration=duration,
                    response_size=len(result.content) if hasattr(result, 'content') else None
                )
                
                return result
            except httpx.HTTPStatusError as e:
                duration = (time.time() - start_time) * 1000
                
                # Log HTTP error
                logger.error(
                    f"API call failed with status {e.response.status_code}: {service_name}",
                    error_category=ErrorCategory.EXTERNAL_API,
                    alert_level="medium" if e.response.status_code >= 500 else "low",
                    operation="external_api_error",
                    service=service_name,
                    endpoint=actual_endpoint or "unknown",
                    status_code=e.response.status_code,
                    duration=duration,
                    error=str(e),
                    response_body=e.response.text[:500] if hasattr(e, 'response') else None
                )
                
                raise
            except httpx.RequestError as e:
                duration = (time.time() - start_time) * 1000
                
                # Log connection error
                logger.error(
                    f"API connection error: {service_name}",
                    error_category=ErrorCategory.EXTERNAL_API,
                    alert_level="medium",
                    operation="external_api_connection_error",
                    service=service_name,
                    endpoint=actual_endpoint or "unknown",
                    duration=duration,
                    error=str(e),
                    exc_info=True
                )
                
                raise
            except Exception as e:
                duration = (time.time() - start_time) * 1000
                
                # Log general error
                logger.error(
                    f"API call failed: {service_name}",
                    error_category=ErrorCategory.EXTERNAL_API,
                    alert_level="medium",
                    operation="external_api_error",
                    service=service_name,
                    endpoint=actual_endpoint or "unknown",
                    duration=duration,
                    error=str(e),
                    exc_info=True
                )
                
                raise
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs) -> T:
            # Extract endpoint from URL if not provided
            nonlocal endpoint
            actual_endpoint = endpoint
            
            # Try to extract endpoint from URL in kwargs
            if not actual_endpoint:
                for param_name in ['url', 'endpoint', 'path']:
                    if param_name in kwargs:
                        url_value = kwargs[param_name]
                        if isinstance(url_value, str):
                            actual_endpoint = url_value.split('?')[0]  # Remove query params
                            break
            
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                duration = (time.time() - start_time) * 1000  # Convert to ms
                
                # Extract status code from response if available
                status_code = None
                if isinstance(result, httpx.Response):
                    status_code = result.status_code
                elif hasattr(result, 'status_code'):
                    status_code = result.status_code
                elif isinstance(result, dict) and 'status_code' in result:
                    status_code = result['status_code']
                
                # Log successful API call
                logger.log_external_api_call(
                    service=service_name,
                    endpoint=actual_endpoint or "unknown",
                    status_code=status_code or 200,
                    duration=duration,
                    response_size=len(result.content) if hasattr(result, 'content') else None
                )
                
                return result
            except httpx.HTTPStatusError as e:
                duration = (time.time() - start_time) * 1000
                
                # Log HTTP error
                logger.error(
                    f"API call failed with status {e.response.status_code}: {service_name}",
                    error_category=ErrorCategory.EXTERNAL_API,
                    alert_level="medium" if e.response.status_code >= 500 else "low",
                    operation="external_api_error",
                    service=service_name,
                    endpoint=actual_endpoint or "unknown",
                    status_code=e.response.status_code,
                    duration=duration,
                    error=str(e),
                    response_body=e.response.text[:500] if hasattr(e, 'response') else None
                )
                
                raise
            except httpx.RequestError as e:
                duration = (time.time() - start_time) * 1000
                
                # Log connection error
                logger.error(
                    f"API connection error: {service_name}",
                    error_category=ErrorCategory.EXTERNAL_API,
                    alert_level="medium",
                    operation="external_api_connection_error",
                    service=service_name,
                    endpoint=actual_endpoint or "unknown",
                    duration=duration,
                    error=str(e),
                    exc_info=True
                )
                
                raise
            except Exception as e:
                duration = (time.time() - start_time) * 1000
                
                # Log general error
                logger.error(
                    f"API call failed: {service_name}",
                    error_category=ErrorCategory.EXTERNAL_API,
                    alert_level="medium",
                    operation="external_api_error",
                    service=service_name,
                    endpoint=actual_endpoint or "unknown",
                    duration=duration,
                    error=str(e),
                    exc_info=True
                )
                
                raise
        
        # Return appropriate wrapper based on whether the function is async
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper
    
    return decorator


class LoggedClient:
    """
    HTTPX client wrapper with automatic logging.
    """
    
    def __init__(self, service_name: str, client: Optional[httpx.AsyncClient] = None):
        """
        Initialize the logged client.
        
        Args:
            service_name: Name of the service for logging
            client: Optional existing HTTPX client to wrap
        """
        self.service_name = service_name
        self.client = client or httpx.AsyncClient()
    
    async def __aenter__(self):
        await self.client.__aenter__()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.__aexit__(exc_type, exc_val, exc_tb)
    
    async def request(self, method: str, url: str, **kwargs) -> httpx.Response:
        """
        Make a request with logging.
        
        Args:
            method: HTTP method
            url: URL to request
            **kwargs: Additional arguments to pass to httpx
        
        Returns:
            HTTPX Response
        """
        start_time = time.time()
        endpoint = url.split('?')[0]  # Remove query params
        
        try:
            response = await self.client.request(method, url, **kwargs)
            duration = (time.time() - start_time) * 1000
            
            # Log response
            logger.log_external_api_call(
                service=self.service_name,
                endpoint=endpoint,
                status_code=response.status_code,
                duration=duration,
                method=method,
                response_size=len(response.content)
            )
            
            return response
        except httpx.HTTPStatusError as e:
            duration = (time.time() - start_time) * 1000
            
            # Log HTTP error
            logger.error(
                f"API call failed with status {e.response.status_code}: {self.service_name}",
                error_category=ErrorCategory.EXTERNAL_API,
                alert_level="medium" if e.response.status_code >= 500 else "low",
                operation="external_api_error",
                service=self.service_name,
                endpoint=endpoint,
                method=method,
                status_code=e.response.status_code,
                duration=duration,
                error=str(e),
                response_body=e.response.text[:500]
            )
            
            raise
        except Exception as e:
            duration = (time.time() - start_time) * 1000
            
            # Log general error
            logger.error(
                f"API call failed: {self.service_name}",
                error_category=ErrorCategory.EXTERNAL_API,
                alert_level="medium",
                operation="external_api_error",
                service=self.service_name,
                endpoint=endpoint,
                method=method,
                duration=duration,
                error=str(e),
                exc_info=True
            )
            
            raise
    
    # Convenience methods for common HTTP methods
    async def get(self, url: str, **kwargs) -> httpx.Response:
        return await self.request("GET", url, **kwargs)
    
    async def post(self, url: str, **kwargs) -> httpx.Response:
        return await self.request("POST", url, **kwargs)
    
    async def put(self, url: str, **kwargs) -> httpx.Response:
        return await self.request("PUT", url, **kwargs)
    
    async def delete(self, url: str, **kwargs) -> httpx.Response:
        return await self.request("DELETE", url, **kwargs)
    
    async def patch(self, url: str, **kwargs) -> httpx.Response:
        return await self.request("PATCH", url, **kwargs)