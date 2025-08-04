"""
Simplified API router for Vercel deployment.
Only includes essential endpoints that are guaranteed to work.
"""

from fastapi import APIRouter
from datetime import datetime

api_router = APIRouter()

@api_router.get("/")
async def root():
    """Root endpoint for API v1."""
    return {
        "message": "Reddit Content Platform API v1",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc",
        "timestamp": datetime.utcnow().isoformat()
    }

@api_router.get("/status")
async def api_status():
    """API status endpoint."""
    return {
        "status": "operational",
        "api_version": "v1",
        "timestamp": datetime.utcnow().isoformat(),
        "endpoints": {
            "health": "/api/v1/health/*",
            "auth": "/api/v1/auth/*",
            "keywords": "/api/v1/keywords/*",
            "posts": "/api/v1/posts/*"
        }
    }

# Try to import and include working endpoints
try:
    from app.api.v1.endpoints import health_simple as health
    api_router.include_router(health.router, prefix="/health", tags=["health"])
except ImportError as e:
    print(f"Warning: Could not import health router: {e}")

try:
    from app.api.v1.endpoints import auth
    api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
except ImportError as e:
    print(f"Warning: Could not import auth router: {e}")

try:
    from app.api.v1.endpoints import keywords
    api_router.include_router(keywords.router, prefix="/keywords", tags=["keywords"])
except ImportError as e:
    print(f"Warning: Could not import keywords router: {e}")

try:
    from app.api.v1.endpoints import posts
    api_router.include_router(posts.router, prefix="/posts", tags=["posts"])
except ImportError as e:
    print(f"Warning: Could not import posts router: {e}")

# Add more endpoints as they become available
# try:
#     from app.api.v1.endpoints import tasks
#     api_router.include_router(tasks.router, prefix="/tasks", tags=["tasks"])
# except ImportError as e:
#     print(f"Warning: Could not import tasks router: {e}")

# try:
#     from app.api.v1.endpoints import trends
#     api_router.include_router(trends.router, prefix="/trends", tags=["trends"])
# except ImportError as e:
#     print(f"Warning: Could not import trends router: {e}")