"""
Post model for storing Reddit posts and comments.
"""

from sqlalchemy import Column, String, Integer, ForeignKey, Text, DateTime, Index
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


class Post(BaseModel):
    """
    Post model for storing Reddit posts.
    Contains post metadata and content from Reddit API.
    """
    __tablename__ = "posts"

    keyword_id = Column(Integer, ForeignKey("keywords.id"), nullable=False, index=True)
    reddit_id = Column(String(50), unique=True, nullable=False, index=True)
    title = Column(String(500), nullable=False)
    content = Column(Text)  # Post body content
    author = Column(String(255), nullable=False)
    score = Column(Integer, default=0, nullable=False)
    num_comments = Column(Integer, default=0, nullable=False)
    url = Column(String(500), nullable=False)
    subreddit = Column(String(255), nullable=False)
    post_created_at = Column(DateTime, nullable=False)  # When post was created on Reddit
    
    # Relationships
    keyword = relationship("Keyword", back_populates="posts")
    comments = relationship("Comment", back_populates="post", cascade="all, delete-orphan")
    metrics = relationship("Metric", back_populates="post", cascade="all, delete-orphan")
    
    # Indexes for performance
    __table_args__ = (
        Index('ix_posts_keyword_score', 'keyword_id', 'score'),
        Index('ix_posts_created_at', 'post_created_at'),
        Index('ix_posts_subreddit', 'subreddit'),
    )

    def __repr__(self):
        return f"<Post(id={self.id}, reddit_id='{self.reddit_id}', title='{self.title[:50]}...')>"


class Comment(BaseModel):
    """
    Comment model for storing Reddit comments.
    Associated with posts for comprehensive content analysis.
    """
    __tablename__ = "comments"

    post_id = Column(Integer, ForeignKey("posts.id"), nullable=False, index=True)
    reddit_id = Column(String(50), unique=True, nullable=False, index=True)
    body = Column(Text, nullable=False)
    author = Column(String(255), nullable=False)
    score = Column(Integer, default=0, nullable=False)
    comment_created_at = Column(DateTime, nullable=False)  # When comment was created on Reddit
    
    # Relationships
    post = relationship("Post", back_populates="comments")
    
    # Indexes for performance
    __table_args__ = (
        Index('ix_comments_post_score', 'post_id', 'score'),
        Index('ix_comments_created_at', 'comment_created_at'),
    )

    def __repr__(self):
        return f"<Comment(id={self.id}, reddit_id='{self.reddit_id}', post_id={self.post_id})>"