"""
API versioning utilities and configuration.
"""

from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse


class APIVersion:
    """API version configuration."""
    
    def __init__(
        self,
        version: str,
        is_default: bool = False,
        is_deprecated: bool = False,
        sunset_date: Optional[datetime] = None,
        description: Optional[str] = None
    ):
        self.version = version
        self.is_default = is_default
        self.is_deprecated = is_deprecated
        self.sunset_date = sunset_date
        self.description = description


# Supported API versions
API_VERSIONS = {
    "v1": APIVersion(
        version="v1",
        is_default=True,
        is_deprecated=False,
        description="Current stable version with full feature support"
    ),
    # Future versions can be added here
    # "v2": APIVersion(
    #     version="v2",
    #     is_default=False,
    #     is_deprecated=False,
    #     description="Next version with enhanced features"
    # ),
}

# Default version
DEFAULT_VERSION = "v1"

# Version header name
VERSION_HEADER = "Accept"
VERSION_MEDIA_TYPE_PREFIX = "application/vnd.reddit-platform"


def get_api_version_from_request(request: Request) -> str:
    """
    Extract API version from request.
    
    Checks in order:
    1. URL path (/api/v1/...)
    2. Accept header (application/vnd.reddit-platform.v1+json)
    3. X-API-Version header
    4. Default version
    """
    # Check URL path
    path = request.url.path
    if path.startswith("/api/"):
        path_parts = path.split("/")
        if len(path_parts) >= 3 and path_parts[2].startswith("v"):
            version = path_parts[2]
            if version in API_VERSIONS:
                return version
    
    # Check Accept header
    accept_header = request.headers.get("Accept", "")
    if VERSION_MEDIA_TYPE_PREFIX in accept_header:
        # Parse application/vnd.reddit-platform.v1+json
        try:
            media_type = accept_header.split(",")[0].strip()
            if VERSION_MEDIA_TYPE_PREFIX in media_type:
                version_part = media_type.split(VERSION_MEDIA_TYPE_PREFIX + ".")[1]
                version = version_part.split("+")[0]
                if version in API_VERSIONS:
                    return version
        except (IndexError, AttributeError):
            pass
    
    # Check X-API-Version header
    version_header = request.headers.get("X-API-Version")
    if version_header and version_header in API_VERSIONS:
        return version_header
    
    # Return default version
    return DEFAULT_VERSION


def validate_api_version(version: str) -> APIVersion:
    """
    Validate and return API version configuration.
    
    Args:
        version: Version string to validate
        
    Returns:
        APIVersion configuration
        
    Raises:
        HTTPException: If version is not supported
    """
    if version not in API_VERSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error_code": "unsupported_version",
                "message": f"API version '{version}' is not supported",
                "supported_versions": list(API_VERSIONS.keys()),
                "default_version": DEFAULT_VERSION
            }
        )
    
    return API_VERSIONS[version]


def add_version_headers(response: JSONResponse, version: str) -> JSONResponse:
    """
    Add version-related headers to response.
    
    Args:
        response: FastAPI response object
        version: API version used
        
    Returns:
        Response with version headers added
    """
    api_version = API_VERSIONS.get(version)
    if not api_version:
        return response
    
    # Add version headers
    response.headers["X-API-Version"] = version
    response.headers["X-API-Version-Default"] = DEFAULT_VERSION
    response.headers["X-API-Versions-Supported"] = ",".join(API_VERSIONS.keys())
    
    # Add deprecation headers if applicable
    if api_version.is_deprecated:
        response.headers["Deprecation"] = "true"
        if api_version.sunset_date:
            response.headers["Sunset"] = api_version.sunset_date.strftime("%a, %d %b %Y %H:%M:%S GMT")
    
    return response


def get_version_info() -> Dict[str, Any]:
    """
    Get comprehensive version information.
    
    Returns:
        Dictionary with version information
    """
    return {
        "default_version": DEFAULT_VERSION,
        "supported_versions": {
            version: {
                "version": config.version,
                "is_default": config.is_default,
                "is_deprecated": config.is_deprecated,
                "sunset_date": config.sunset_date.isoformat() if config.sunset_date else None,
                "description": config.description
            }
            for version, config in API_VERSIONS.items()
        },
        "version_header": VERSION_HEADER,
        "media_type_prefix": VERSION_MEDIA_TYPE_PREFIX,
        "examples": {
            "url_versioning": "/api/v1/keywords",
            "header_versioning": f"{VERSION_MEDIA_TYPE_PREFIX}.v1+json",
            "custom_header": "X-API-Version: v1"
        }
    }


class VersioningMiddleware:
    """Middleware to handle API versioning."""
    
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            request = Request(scope, receive)
            
            # Get and validate version
            try:
                version = get_api_version_from_request(request)
                api_version = validate_api_version(version)
                
                # Add version info to request state
                request.state.api_version = version
                request.state.api_version_config = api_version
                
                # Check for deprecated version warnings
                if api_version.is_deprecated:
                    # Log deprecation warning
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.warning(
                        f"Deprecated API version {version} used",
                        extra={
                            "api_version": version,
                            "sunset_date": api_version.sunset_date.isoformat() if api_version.sunset_date else None,
                            "user_agent": request.headers.get("User-Agent"),
                            "client_ip": request.client.host if request.client else None
                        }
                    )
                
                # Create a custom send function to add version headers
                async def send_with_version_headers(message):
                    if message["type"] == "http.response.start":
                        headers = dict(message.get("headers", []))
                        
                        # Add version headers
                        headers[b"x-api-version"] = version.encode()
                        headers[b"x-api-version-default"] = DEFAULT_VERSION.encode()
                        headers[b"x-api-versions-supported"] = ",".join(API_VERSIONS.keys()).encode()
                        
                        # Add deprecation headers if applicable
                        if api_version.is_deprecated:
                            headers[b"deprecation"] = b"true"
                            if api_version.sunset_date:
                                headers[b"sunset"] = api_version.sunset_date.strftime("%a, %d %b %Y %H:%M:%S GMT").encode()
                        
                        # Add API documentation links
                        headers[b"link"] = f'</docs>; rel="help", </redoc>; rel="alternate"'.encode()
                        
                        message["headers"] = [(k.encode() if isinstance(k, str) else k, 
                                            v.encode() if isinstance(v, str) else v) 
                                           for k, v in headers.items()]
                    
                    await send(message)
                
                await self.app(scope, receive, send_with_version_headers)
                
            except HTTPException as e:
                # Return version error response with proper headers
                response = JSONResponse(
                    status_code=e.status_code,
                    content=e.detail
                )
                
                # Add version headers to error response
                response.headers["X-API-Version-Default"] = DEFAULT_VERSION
                response.headers["X-API-Versions-Supported"] = ",".join(API_VERSIONS.keys())
                response.headers["Link"] = '</docs>; rel="help", </redoc>; rel="alternate"'
                
                await response(scope, receive, send)
                return
        else:
            await self.app(scope, receive, send)


def create_version_aware_response(content: Any, status_code: int = 200, 
                                headers: Optional[Dict[str, str]] = None,
                                version: Optional[str] = None) -> JSONResponse:
    """
    Create a version-aware JSON response with appropriate headers.
    
    Args:
        content: Response content
        status_code: HTTP status code
        headers: Additional headers
        version: API version (if not provided, uses default)
        
    Returns:
        JSONResponse with version headers
    """
    response = JSONResponse(content=content, status_code=status_code, headers=headers)
    
    # Add version headers
    if version is None:
        version = DEFAULT_VERSION
    
    response.headers["X-API-Version"] = version
    response.headers["X-API-Version-Default"] = DEFAULT_VERSION
    response.headers["X-API-Versions-Supported"] = ",".join(API_VERSIONS.keys())
    
    # Add deprecation headers if applicable
    api_version = API_VERSIONS.get(version)
    if api_version and api_version.is_deprecated:
        response.headers["Deprecation"] = "true"
        if api_version.sunset_date:
            response.headers["Sunset"] = api_version.sunset_date.strftime("%a, %d %b %Y %H:%M:%S GMT")
    
    # Add documentation links
    response.headers["Link"] = '</docs>; rel="help", </redoc>; rel="alternate"'
    
    return response