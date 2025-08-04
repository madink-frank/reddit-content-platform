"""
Blog content model for storing generated markdown content.
"""

from sqlalchemy import Column, String, Integer, ForeignKey, Text, DateTime, Index
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


class BlogContent(BaseModel):
    """
    BlogContent model for storing generated markdown blog posts.
    Contains content generated from trend analysis.
    """
    __tablename__ = "blog_contents"

    keyword_id = Column(Integer, ForeignKey("keywords.id"), nullable=False, index=True)
    title = Column(String(500), nullable=False)
    content = Column(Text, nullable=False)  # Markdown formatted content
    template_used = Column(String(100), nullable=False)
    generated_at = Column(DateTime, nullable=False)
    
    # Additional metadata
    word_count = Column(Integer, default=0)
    status = Column(String(50), default="draft")  # draft, published, archived
    slug = Column(String(255))  # URL-friendly version of title
    tags = Column(Text)  # JSON array of tags
    
    # SEO and metadata
    meta_description = Column(String(500))
    featured_image_url = Column(String(500))
    
    # Relationships
    keyword = relationship("Keyword", back_populates="blog_contents")
    
    # Indexes for performance
    __table_args__ = (
        Index('ix_blog_contents_keyword_generated', 'keyword_id', 'generated_at'),
        Index('ix_blog_contents_status', 'status'),
        Index('ix_blog_contents_slug', 'slug'),
    )

    def __repr__(self):
        return f"<BlogContent(id={self.id}, keyword_id={self.keyword_id}, title='{self.title[:50]}...', status='{self.status}')>"