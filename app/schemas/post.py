"""
Post schemas for API request/response models.
"""

from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field


class CommentResponse(BaseModel):
    """Response model for comments."""
    id: int
    reddit_id: str
    body: str
    author: str
    score: int
    comment_created_at: datetime
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PostResponse(BaseModel):
    """Response model for posts."""
    id: int
    keyword_id: int
    reddit_id: str
    title: str
    content: Optional[str] = None
    author: str
    score: int
    num_comments: int
    url: str
    subreddit: str
    post_created_at: datetime
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PostDetailResponse(PostResponse):
    """Detailed post response including comments."""
    comments: List[CommentResponse] = []

    class Config:
        from_attributes = True


class PostListResponse(BaseModel):
    """Paginated post list response."""
    posts: List[PostResponse]
    total: int
    page: int
    per_page: int
    total_pages: int
    has_next: bool
    has_prev: bool

    class Config:
        from_attributes = True


class PostQueryParams(BaseModel):
    """Query parameters for post filtering and pagination."""
    page: int = Field(1, ge=1, description="Page number")
    per_page: int = Field(10, ge=1, le=100, description="Items per page")
    keyword_id: Optional[int] = Field(None, description="Filter by keyword ID")
    subreddit: Optional[str] = Field(None, description="Filter by subreddit")
    author: Optional[str] = Field(None, description="Filter by author")
    search: Optional[str] = Field(None, description="Search in title and content")
    sort_by: str = Field("created_at", description="Sort field")
    sort_order: str = Field("desc", pattern="^(asc|desc)$", description="Sort order")
    min_score: Optional[int] = Field(None, description="Minimum score filter")
    max_score: Optional[int] = Field(None, description="Maximum score filter")
    date_from: Optional[datetime] = Field(None, description="Filter posts from this date")
    date_to: Optional[datetime] = Field(None, description="Filter posts to this date")