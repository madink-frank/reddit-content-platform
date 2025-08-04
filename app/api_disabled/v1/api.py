"""
Main API router that includes all endpoint routers.
"""

from fastapi import APIRouter

# Import routers
from app.api.v1.endpoints import auth
from app.api.v1.endpoints import keywords
from app.api.v1.endpoints import tasks
from app.api.v1.endpoints import reddit
from app.api.v1.endpoints import crawling
from app.api.v1.endpoints import posts
from app.api.v1.endpoints import trends
from app.api.v1.endpoints import content
from app.api.v1.endpoints import public_blog
from app.api.v1.endpoints import health
from app.api.v1.endpoints import system
# from app.api.v1.endpoints import analytics, deployment

api_router = APIRouter()

# Include routers
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(keywords.router, prefix="/keywords", tags=["keywords"])
api_router.include_router(tasks.router, prefix="/tasks", tags=["tasks"])
api_router.include_router(reddit.router, prefix="/reddit", tags=["reddit"])
api_router.include_router(crawling.router, prefix="/crawling", tags=["crawling"])
api_router.include_router(posts.router, prefix="/posts", tags=["posts"])
api_router.include_router(trends.router, prefix="/trends", tags=["trends"])
api_router.include_router(content.router, prefix="/content", tags=["content"])
api_router.include_router(public_blog.router, prefix="/blog", tags=["public-blog"])
api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(system.router, prefix="/system", tags=["system"])
# api_router.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
# api_router.include_router(deployment.router, prefix="/deployment", tags=["deployment"])

@api_router.get("/")
async def root():
    """Root endpoint for API v1."""
    return {
        "message": "Reddit Content Platform API v1",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc"
    }