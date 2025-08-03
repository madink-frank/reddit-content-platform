"""
Keyword model for user-defined search terms.
"""

from sqlalchemy import Column, String, Boolean, Integer, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


class Keyword(BaseModel):
    """
    Keyword model for storing user-defined search terms.
    Each user can have multiple keywords for Reddit content crawling.
    """
    __tablename__ = "keywords"

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    keyword = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="keywords")
    posts = relationship("Post", back_populates="keyword", cascade="all, delete-orphan")
    blog_contents = relationship("BlogContent", back_populates="keyword", cascade="all, delete-orphan")
    
    # Constraints
    __table_args__ = (
        UniqueConstraint('user_id', 'keyword', name='uq_user_keyword'),
    )

    def __repr__(self):
        return f"<Keyword(id={self.id}, user_id={self.user_id}, keyword='{self.keyword}', active={self.is_active})>"