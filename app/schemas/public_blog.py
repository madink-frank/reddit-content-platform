"""
Public blog schemas for API serialization and validation.
These schemas are used for public-facing blog endpoints that don't require authentication.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class PublicBlogPostBase(BaseModel):
    """Base schema for public blog post."""
    title: str = Field(..., description="Blog post title")
    content: str = Field(..., description="Markdown formatted content")
    slug: str = Field(..., description="URL-friendly slug")
    meta_description: Optional[str] = Field(None, description="SEO meta description")
    tags: List[str] = Field(default_factory=list, description="Content tags")
    featured_image_url: Optional[str] = Field(None, description="Featured image URL")
    word_count: int = Field(..., description="Content word count")
    estimated_read_time: int = Field(..., description="Estimated read time in minutes")


class PublicBlogPostSummary(BaseModel):
    """Schema for blog post summary in list views."""
    id: int
    title: str
    slug: str
    meta_description: Optional[str]
    tags: List[str]
    featured_image_url: Optional[str]
    word_count: int
    estimated_read_time: int
    published_at: datetime
    excerpt: str = Field(..., description="First 200 characters of content")
    
    class Config:
        from_attributes = True


class PublicBlogPostDetail(PublicBlogPostBase):
    """Schema for detailed blog post view."""
    id: int
    published_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class PublicBlogPostListResponse(BaseModel):
    """Schema for paginated blog post list."""
    posts: List[PublicBlogPostSummary]
    total: int
    page: int
    size: int
    pages: int
    has_next: bool
    has_prev: bool


class BlogCategoryResponse(BaseModel):
    """Schema for blog categories."""
    name: str
    slug: str
    count: int
    description: Optional[str] = None


class BlogTagResponse(BaseModel):
    """Schema for blog tags."""
    name: str
    slug: str
    count: int


class BlogSearchResponse(BaseModel):
    """Schema for blog search results."""
    posts: List[PublicBlogPostSummary]
    total: int
    query: str
    page: int
    size: int
    pages: int
    search_time_ms: int


class BlogArchiveResponse(BaseModel):
    """Schema for blog archive by date."""
    year: int
    month: int
    count: int
    posts: List[PublicBlogPostSummary]


class BlogStatsResponse(BaseModel):
    """Schema for blog statistics."""
    total_posts: int
    total_words: int
    total_tags: int
    latest_post_date: Optional[datetime]
    average_read_time: float


class RSSFeedItem(BaseModel):
    """Schema for RSS feed item."""
    title: str
    link: str
    description: str
    pub_date: datetime
    guid: str


class RSSFeedResponse(BaseModel):
    """Schema for RSS feed."""
    title: str
    link: str
    description: str
    language: str
    last_build_date: datetime
    items: List[RSSFeedItem]


class SitemapUrl(BaseModel):
    """Schema for sitemap URL."""
    loc: str
    lastmod: datetime
    changefreq: str = "weekly"
    priority: float = 0.5


class SitemapResponse(BaseModel):
    """Schema for sitemap."""
    urls: List[SitemapUrl]


class RelatedPostResponse(BaseModel):
    """Schema for related posts."""
    id: int
    title: str
    slug: str
    excerpt: str
    published_at: datetime
    similarity_score: float = Field(..., description="Similarity score based on tags and content")
    
    class Config:
        from_attributes = True