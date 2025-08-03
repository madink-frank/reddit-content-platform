import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from app.core.config import settings
from app.api.v1.api import api_router
from app.core.metrics import PrometheusMiddleware, get_metrics_response
from app.core.openapi_config import get_openapi_config, get_enhanced_openapi_examples, get_api_documentation_config, get_api_schema_examples
from app.core.system_metrics import start_metrics_collection, stop_metrics_collection
from app.core.logging import setup_logging, configure_advanced_logging, get_logger
from app.core.middleware import RequestTrackingMiddleware, LoggingMiddleware, ErrorHandlingMiddleware
from app.core.versioning import VersioningMiddleware, get_version_info
from app.core.performance_middleware import (
    PerformanceMiddleware, 
    CacheMiddleware, 
    RateLimitingMiddleware
)
from app.core.database_optimization import QueryOptimizer
from app.core.cache_optimization import initialize_cache_warmup

# Setup logging before creating the app
setup_logging()
configure_advanced_logging()

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    logger.info("Starting Reddit Content Platform API", operation="app_startup")
    
    if settings.ENVIRONMENT != "test":
        # Create performance indexes
        try:
            QueryOptimizer.create_performance_indexes()
            logger.info("Created performance indexes", operation="db_optimization")
        except Exception as e:
            logger.error(f"Failed to create performance indexes: {e}", operation="db_optimization")
        
        # Initialize cache warmup
        try:
            await initialize_cache_warmup()
            logger.info("Initialized cache warmup", operation="cache_optimization")
        except Exception as e:
            logger.error(f"Failed to initialize cache warmup: {e}", operation="cache_optimization")
        
        # Start metrics collection in background
        metrics_task = asyncio.create_task(start_metrics_collection(30))
        logger.info("Started metrics collection", operation="metrics_startup")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Reddit Content Platform API", operation="app_shutdown")
    
    if settings.ENVIRONMENT != "test":
        stop_metrics_collection()
        if 'metrics_task' in locals():
            metrics_task.cancel()
            try:
                await metrics_task
            except asyncio.CancelledError:
                pass
        logger.info("Stopped metrics collection", operation="metrics_shutdown")

def custom_openapi():
    """Custom OpenAPI schema with enhanced documentation."""
    if app.openapi_schema:
        return app.openapi_schema
    
    # Get configuration from centralized config
    config = get_openapi_config()
    
    openapi_schema = get_openapi(
        title=config["title"],
        version=config["version"],
        description=config["description"],
        routes=app.routes,
        tags=config["tags"]
    )
    
    # Add security schemes
    openapi_schema["components"]["securitySchemes"] = config["security_schemes"]
    
    # Add servers information
    openapi_schema["servers"] = config["servers"]
    
    # Add contact and license information
    openapi_schema["info"]["contact"] = config["contact"]
    openapi_schema["info"]["license"] = config["license"]
    
    # Add external documentation
    openapi_schema["externalDocs"] = config["external_docs"]
    
    # Add common response schemas
    if "components" not in openapi_schema:
        openapi_schema["components"] = {}
    if "responses" not in openapi_schema["components"]:
        openapi_schema["components"]["responses"] = {}
    if "schemas" not in openapi_schema["components"]:
        openapi_schema["components"]["schemas"] = {}
    
    # Add common responses
    openapi_schema["components"]["responses"].update(config["common_responses"])
    
    # Add example schemas
    openapi_schema["components"]["schemas"].update(config["example_schemas"])
    
    # Add API versioning information
    openapi_schema["info"]["x-api-version"] = settings.VERSION
    openapi_schema["info"]["x-api-versions-supported"] = ["v1"]
    openapi_schema["info"]["x-api-version-header"] = "X-API-Version"
    openapi_schema["info"]["x-api-media-type"] = "application/vnd.reddit-platform.v1+json"
    
    # Get enhanced documentation configuration
    doc_config = get_api_documentation_config()
    enhanced_examples = get_enhanced_openapi_examples()
    schema_examples = get_api_schema_examples()
    
    # Add enhanced documentation features
    openapi_schema["x-tagGroups"] = doc_config["x-tagGroups"]
    openapi_schema["x-code-samples"] = doc_config["x-code-samples"]
    
    # Add enhanced examples
    openapi_schema["x-examples"] = enhanced_examples
    openapi_schema["x-schema-examples"] = schema_examples
    
    # Add rate limiting information
    openapi_schema["x-rate-limits"] = {
        "general": "60 requests per minute per user",
        "reddit_api": "60 requests per minute (shared)",
        "content_generation": "10 requests per hour per user",
        "public_api": "100 requests per minute per IP"
    }
    
    # Add API usage guidelines
    openapi_schema["x-api-guidelines"] = {
        "authentication": {
            "description": "All endpoints except public blog API require authentication",
            "token_lifetime": "Access tokens expire in 15 minutes, refresh tokens in 7 days",
            "best_practices": [
                "Store tokens securely",
                "Implement automatic token refresh",
                "Handle 401 responses gracefully"
            ]
        },
        "pagination": {
            "description": "List endpoints support pagination",
            "parameters": ["page", "page_size", "limit", "offset"],
            "max_page_size": 100,
            "default_page_size": 20
        },
        "error_handling": {
            "description": "All errors follow consistent format",
            "include_request_id": True,
            "retry_strategy": "Exponential backoff for 5xx errors"
        }
    }
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app = FastAPI(
    title="Reddit Content Platform API",
    version=settings.VERSION,
    description="Reddit Content Crawling and Trend Analysis Platform",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
    openapi_tags=[
        {
            "name": "authentication",
            "description": "Reddit OAuth2 authentication and JWT token management"
        },
        {
            "name": "keywords", 
            "description": "Keyword management for tracking specific topics on Reddit"
        },
        {
            "name": "crawling",
            "description": "Reddit content crawling operations and status monitoring"
        },
        {
            "name": "posts",
            "description": "Search and retrieve crawled Reddit posts with filtering options"
        },
        {
            "name": "analytics",
            "description": "Trend analysis and statistics from collected Reddit data"
        },
        {
            "name": "content",
            "description": "AI-powered content generation based on analyzed data"
        },
        {
            "name": "monitoring",
            "description": "System health monitoring and metrics"
        }
    ]
)

# Set custom OpenAPI schema
app.openapi = custom_openapi

# Add middleware in correct order (last added = first executed)
# CORS middleware (outermost)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate limiting middleware
app.add_middleware(RateLimitingMiddleware, requests_per_minute=60)

# Performance monitoring middleware
app.add_middleware(PerformanceMiddleware, slow_request_threshold=1.0)

# Response caching middleware
app.add_middleware(CacheMiddleware, cache_ttl=300)

# API versioning middleware
app.add_middleware(VersioningMiddleware)

# Error handling middleware
app.add_middleware(ErrorHandlingMiddleware)

# Request tracking middleware
app.add_middleware(RequestTrackingMiddleware)

# Logging middleware (optional, for detailed request/response logging)
if settings.LOG_LEVEL.upper() == "DEBUG":
    app.add_middleware(LoggingMiddleware, log_requests=True, log_responses=False)

# Prometheus metrics middleware (innermost, closest to the application)
app.middleware("http")(PrometheusMiddleware())

# Include API router
app.include_router(api_router, prefix=settings.API_V1_STR)

# Metrics endpoint
@app.get(
    "/metrics",
    tags=["monitoring"],
    summary="Get Prometheus metrics",
    description="Retrieve Prometheus-formatted metrics for monitoring system performance and health.",
    responses={
        200: {
            "description": "Prometheus metrics in text format",
            "content": {"text/plain": {"example": "# HELP api_requests_total Total API requests\n# TYPE api_requests_total counter\napi_requests_total{method=\"GET\",endpoint=\"/health\"} 42"}}
        }
    }
)
async def metrics():
    """Prometheus metrics endpoint for system monitoring."""
    return get_metrics_response()

@app.get(
    "/health",
    tags=["monitoring"],
    summary="Basic health check",
    description="Simple health check endpoint that returns the basic status of the service.",
    responses={
        200: {
            "description": "Service is healthy",
            "content": {
                "application/json": {
                    "example": {"status": "healthy", "service": "reddit-content-platform"}
                }
            }
        }
    }
)
async def health_check():
    """Basic health check endpoint."""
    return {"status": "healthy", "service": "reddit-content-platform"}

@app.get(
    "/health/detailed",
    tags=["monitoring"],
    summary="Detailed health check",
    description="Comprehensive health check that verifies the status of all system components including database, Redis, and Celery workers.",
    responses={
        200: {
            "description": "Detailed health status of all components",
            "content": {
                "application/json": {
                    "example": {
                        "status": "healthy",
                        "timestamp": "2024-01-01T00:00:00Z",
                        "services": {
                            "database": {"status": "healthy", "response_time_ms": 5},
                            "redis": {"status": "healthy", "response_time_ms": 2},
                            "celery": {"status": "healthy", "active_workers": 3}
                        }
                    }
                }
            }
        },
        503: {
            "description": "One or more services are unhealthy",
            "content": {
                "application/json": {
                    "example": {
                        "status": "unhealthy",
                        "timestamp": "2024-01-01T00:00:00Z",
                        "services": {
                            "database": {"status": "unhealthy", "error": "Connection timeout"}
                        }
                    }
                }
            }
        }
    }
)
async def detailed_health_check():
    """Detailed health check endpoint with all system components."""
    from datetime import datetime
    from app.core.system_metrics import check_database_health, check_redis_health, check_celery_health
    
    # Check all services
    database_health = await check_database_health()
    redis_health = await check_redis_health()
    celery_health = await check_celery_health()
    
    services = {
        "database": database_health,
        "redis": redis_health,
        "celery": celery_health
    }
    
    # Determine overall status
    overall_status = "healthy"
    for service_status in services.values():
        if service_status.get("status") != "healthy":
            overall_status = "unhealthy"
            break
    
    response = {
        "status": overall_status,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "services": services
    }
    
    # Return appropriate status code
    if overall_status == "healthy":
        return response
    else:
        from fastapi import HTTPException
        raise HTTPException(status_code=503, detail=response)

@app.get(
    "/health/{service_name}",
    tags=["monitoring"],
    summary="Service-specific health check",
    description="Check the health status of a specific service component (database, redis, celery).",
    responses={
        200: {
            "description": "Service health status",
            "content": {
                "application/json": {
                    "example": {
                        "service": "database",
                        "status": "healthy",
                        "response_time_ms": 5,
                        "details": {"connection_pool": "active", "queries_per_second": 150}
                    }
                }
            }
        },
        404: {
            "description": "Service not found",
            "content": {
                "application/json": {
                    "example": {"error": "service_not_found", "detail": "Service 'unknown' not found"}
                }
            }
        }
    }
)
async def service_health_check(service_name: str):
    """Health check for a specific service."""
    from fastapi import HTTPException
    from app.core.system_metrics import check_database_health, check_redis_health, check_celery_health
    
    service_checks = {
        "database": check_database_health,
        "redis": check_redis_health,
        "celery": check_celery_health
    }
    
    if service_name not in service_checks:
        raise HTTPException(
            status_code=404,
            detail={"error": "service_not_found", "detail": f"Service '{service_name}' not found"}
        )
    
    health_check = service_checks[service_name]
    result = await health_check()
    
    return {
        "service": service_name,
        **result
    }

@app.get(
    "/api/version",
    tags=["monitoring"],
    summary="Get API version information",
    description="Retrieve comprehensive API version information including supported versions, deprecation status, and usage examples.",
    responses={
        200: {
            "description": "API version information",
            "content": {
                "application/json": {
                    "example": {
                        "current_version": "v1",
                        "default_version": "v1",
                        "supported_versions": {
                            "v1": {
                                "version": "v1",
                                "is_default": True,
                                "is_deprecated": False,
                                "description": "Current stable version with full feature support"
                            }
                        },
                        "version_header": "Accept",
                        "media_type_prefix": "application/vnd.reddit-platform",
                        "examples": {
                            "url_versioning": "/api/v1/keywords",
                            "header_versioning": "application/vnd.reddit-platform.v1+json",
                            "custom_header": "X-API-Version: v1"
                        }
                    }
                }
            }
        }
    }
)
async def get_api_version_info():
    """Get comprehensive API version information."""
    return get_version_info()

@app.get(
    "/api/docs/examples",
    tags=["monitoring"],
    summary="Get API usage examples",
    description="Retrieve comprehensive examples for using the API including authentication, common workflows, and best practices.",
    responses={
        200: {
            "description": "API usage examples and documentation",
            "content": {
                "application/json": {
                    "example": {
                        "authentication": {
                            "oauth2_flow": "GET /api/v1/auth/login -> POST /api/v1/auth/login",
                            "token_usage": "Authorization: Bearer <access_token>",
                            "token_refresh": "POST /api/v1/auth/refresh"
                        },
                        "common_workflows": {
                            "basic_setup": ["Create keywords", "Start crawling", "View results"],
                            "content_generation": ["Analyze trends", "Generate content", "Retrieve content"]
                        }
                    }
                }
            }
        }
    }
)
async def get_api_examples():
    """Get comprehensive API usage examples."""
    return {
        "authentication": {
            "oauth2_flow": {
                "step_1": {
                    "description": "Initiate Reddit OAuth2 flow",
                    "method": "GET",
                    "endpoint": "/api/v1/auth/login",
                    "response": "Redirects to Reddit authorization page"
                },
                "step_2": {
                    "description": "Complete authentication with authorization code",
                    "method": "POST",
                    "endpoint": "/api/v1/auth/login",
                    "body": {
                        "code": "authorization_code_from_reddit",
                        "state": "state_parameter"
                    },
                    "response": {
                        "access_token": "jwt_access_token",
                        "refresh_token": "jwt_refresh_token",
                        "expires_in": 900
                    }
                }
            },
            "token_usage": {
                "header": "Authorization: Bearer <access_token>",
                "example": "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
            },
            "token_refresh": {
                "method": "POST",
                "endpoint": "/api/v1/auth/refresh",
                "headers": {"Authorization": "Bearer <refresh_token>"},
                "response": {"access_token": "new_jwt_access_token"}
            }
        },
        "common_workflows": {
            "basic_setup": {
                "description": "Complete workflow from setup to viewing results",
                "steps": [
                    {
                        "step": 1,
                        "action": "Create keywords",
                        "method": "POST",
                        "endpoint": "/api/v1/keywords",
                        "body": {"keyword": "artificial intelligence", "description": "AI discussions"}
                    },
                    {
                        "step": 2,
                        "action": "Start crawling",
                        "method": "POST",
                        "endpoint": "/api/v1/crawling/start",
                        "body": {"keyword_ids": [1], "limit": 100}
                    },
                    {
                        "step": 3,
                        "action": "Check crawling status",
                        "method": "GET",
                        "endpoint": "/api/v1/crawling/status"
                    },
                    {
                        "step": 4,
                        "action": "View collected posts",
                        "method": "GET",
                        "endpoint": "/api/v1/posts?keyword_ids=1"
                    }
                ]
            },
            "content_generation": {
                "description": "Generate content based on collected data",
                "steps": [
                    {
                        "step": 1,
                        "action": "Analyze trends",
                        "method": "GET",
                        "endpoint": "/api/v1/trends?keyword_ids=1&time_period=7d"
                    },
                    {
                        "step": 2,
                        "action": "Generate content",
                        "method": "POST",
                        "endpoint": "/api/v1/content/generate",
                        "body": {
                            "content_type": "blog_post",
                            "keyword_ids": [1],
                            "template_id": 1
                        }
                    },
                    {
                        "step": 3,
                        "action": "Check generation status",
                        "method": "GET",
                        "endpoint": "/api/v1/content/tasks/{task_id}/status"
                    },
                    {
                        "step": 4,
                        "action": "Retrieve generated content",
                        "method": "GET",
                        "endpoint": "/api/v1/content/{content_id}"
                    }
                ]
            }
        },
        "pagination": {
            "description": "How to handle paginated responses",
            "parameters": {
                "page": "Page number (starts from 1)",
                "page_size": "Items per page (max 100)",
                "limit": "Alternative: number of items to return",
                "offset": "Alternative: number of items to skip"
            },
            "example_request": "/api/v1/posts?page=2&page_size=20",
            "example_response": {
                "data": ["..."],
                "pagination": {
                    "page": 2,
                    "per_page": 20,
                    "total": 150,
                    "pages": 8,
                    "has_next": True,
                    "has_prev": True
                }
            }
        },
        "error_handling": {
            "description": "Standard error response format",
            "format": {
                "error_code": "validation_error|unauthorized|forbidden|not_found|rate_limit|internal_error",
                "message": "Human readable error message",
                "details": {"field_name": ["Specific validation errors"]},
                "timestamp": "2024-01-01T00:00:00Z",
                "request_id": "uuid-v4-string"
            },
            "common_errors": {
                "401": "Missing or invalid access token",
                "403": "Valid token but insufficient permissions",
                "422": "Request data validation failed",
                "429": "Rate limit exceeded",
                "500": "Internal server error"
            }
        },
        "rate_limits": {
            "general_api": "60 requests per minute per user",
            "reddit_api": "60 requests per minute (shared across all users)",
            "content_generation": "10 requests per hour per user",
            "public_blog_api": "100 requests per minute per IP (no auth required)",
            "headers": {
                "X-RateLimit-Limit": "Request limit per window",
                "X-RateLimit-Remaining": "Remaining requests in current window",
                "X-RateLimit-Reset": "Unix timestamp when limit resets"
            }
        },
        "best_practices": {
            "authentication": [
                "Store tokens securely",
                "Implement automatic token refresh",
                "Handle token expiration gracefully",
                "Use HTTPS in production"
            ],
            "api_usage": [
                "Use pagination for large datasets",
                "Implement exponential backoff for retries",
                "Cache responses when appropriate",
                "Monitor rate limits",
                "Use specific error handling for different status codes"
            ],
            "performance": [
                "Use bulk operations when available",
                "Filter results at the API level",
                "Use async/await for concurrent requests",
                "Implement request timeouts"
            ]
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)