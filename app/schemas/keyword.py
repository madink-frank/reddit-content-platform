"""
Pydantic schemas for keyword management.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, validator


class KeywordBase(BaseModel):
    """Base keyword schema with common fields."""
    keyword: str = Field(..., min_length=1, max_length=255, description="The keyword to track")
    is_active: bool = Field(default=True, description="Whether the keyword is active for crawling")


class KeywordCreate(KeywordBase):
    """Schema for creating a new keyword."""
    
    @validator('keyword')
    def validate_keyword(cls, v):
        """Validate keyword format."""
        if not v or not v.strip():
            raise ValueError('Keyword cannot be empty or whitespace only')
        # Remove extra whitespace and convert to lowercase for consistency
        return v.strip().lower()


class KeywordUpdate(BaseModel):
    """Schema for updating an existing keyword."""
    keyword: Optional[str] = Field(None, min_length=1, max_length=255, description="The keyword to track")
    is_active: Optional[bool] = Field(None, description="Whether the keyword is active for crawling")
    
    @validator('keyword')
    def validate_keyword(cls, v):
        """Validate keyword format if provided."""
        if v is not None:
            if not v or not v.strip():
                raise ValueError('Keyword cannot be empty or whitespace only')
            # Remove extra whitespace and convert to lowercase for consistency
            return v.strip().lower()
        return v


class KeywordResponse(KeywordBase):
    """Schema for keyword responses."""
    id: int = Field(..., description="Unique identifier for the keyword")
    user_id: int = Field(..., description="ID of the user who owns this keyword")
    created_at: datetime = Field(..., description="When the keyword was created")
    updated_at: datetime = Field(..., description="When the keyword was last updated")
    
    class Config:
        from_attributes = True


class KeywordListResponse(BaseModel):
    """Schema for paginated keyword list responses."""
    keywords: list[KeywordResponse] = Field(..., description="List of keywords")
    total: int = Field(..., description="Total number of keywords")
    page: int = Field(..., description="Current page number")
    per_page: int = Field(..., description="Number of items per page")
    total_pages: int = Field(..., description="Total number of pages")