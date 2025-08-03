"""
Blog content schemas for API serialization and validation.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, validator


class BlogContentBase(BaseModel):
    """Base schema for blog content."""
    title: str = Field(..., min_length=1, max_length=500, description="Blog post title")
    content: str = Field(..., min_length=1, description="Markdown formatted content")
    template_used: str = Field(..., max_length=100, description="Template used for generation")
    meta_description: Optional[str] = Field(None, max_length=500, description="SEO meta description")
    tags: Optional[List[str]] = Field(default_factory=list, description="Content tags")
    featured_image_url: Optional[str] = Field(None, max_length=500, description="Featured image URL")


class BlogContentCreate(BlogContentBase):
    """Schema for creating blog content."""
    keyword_id: int = Field(..., description="Associated keyword ID")
    
    @validator('tags')
    def validate_tags(cls, v):
        if v and len(v) > 10:
            raise ValueError('Maximum 10 tags allowed')
        return v


class BlogContentUpdate(BaseModel):
    """Schema for updating blog content."""
    title: Optional[str] = Field(None, min_length=1, max_length=500)
    content: Optional[str] = Field(None, min_length=1)
    meta_description: Optional[str] = Field(None, max_length=500)
    tags: Optional[List[str]] = None
    featured_image_url: Optional[str] = Field(None, max_length=500)
    status: Optional[str] = Field(None, pattern="^(draft|published|archived)$")
    
    @validator('tags')
    def validate_tags(cls, v):
        if v and len(v) > 10:
            raise ValueError('Maximum 10 tags allowed')
        return v


class BlogContentResponse(BlogContentBase):
    """Schema for blog content response."""
    id: int
    keyword_id: int
    generated_at: datetime
    word_count: int
    status: str
    slug: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class BlogContentListResponse(BaseModel):
    """Schema for paginated blog content list."""
    items: List[BlogContentResponse]
    total: int
    page: int
    size: int
    pages: int


class ContentGenerationRequest(BaseModel):
    """Schema for content generation request."""
    keyword_id: int = Field(..., description="Keyword ID to generate content for")
    template_type: str = Field(default="default", description="Template type to use")
    include_trends: bool = Field(default=True, description="Include trend analysis in content")
    include_top_posts: bool = Field(default=True, description="Include top posts in content")
    max_posts: int = Field(default=10, ge=1, le=50, description="Maximum posts to include")
    custom_prompt: Optional[str] = Field(None, max_length=1000, description="Custom generation prompt")


class ContentGenerationResponse(BaseModel):
    """Schema for content generation response."""
    task_id: str = Field(..., description="Celery task ID")
    status: str = Field(..., description="Task status")
    message: str = Field(..., description="Status message")
    estimated_completion: Optional[datetime] = Field(None, description="Estimated completion time")


class ContentGenerationStatus(BaseModel):
    """Schema for content generation status."""
    task_id: str
    status: str  # pending, running, completed, failed
    progress: int = Field(ge=0, le=100, description="Progress percentage")
    message: str
    result: Optional[BlogContentResponse] = None
    error: Optional[str] = None
    created_at: datetime
    completed_at: Optional[datetime] = None


class TemplateInfo(BaseModel):
    """Schema for template information."""
    name: str
    description: str
    variables: List[str]
    example: Optional[str] = None


class TemplateListResponse(BaseModel):
    """Schema for template list response."""
    templates: List[TemplateInfo]


class ContentPreview(BaseModel):
    """Schema for content preview."""
    title: str
    content_preview: str = Field(..., description="First 500 characters of content")
    word_count: int
    estimated_read_time: int = Field(..., description="Estimated read time in minutes")
    tags: List[str]
    template_used: str