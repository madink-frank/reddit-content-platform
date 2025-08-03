"""
Metric model for storing trend analysis results.
"""

from sqlalchemy import Column, Float, Integer, ForeignKey, DateTime, Index
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


class Metric(BaseModel):
    """
    Metric model for storing trend analysis results.
    Contains TF-IDF scores and engagement metrics for posts.
    """
    __tablename__ = "metrics"

    post_id = Column(Integer, ForeignKey("posts.id"), nullable=False, index=True)
    engagement_score = Column(Float, nullable=False, default=0.0)
    tfidf_score = Column(Float, nullable=False, default=0.0)
    trend_velocity = Column(Float, nullable=False, default=0.0)
    calculated_at = Column(DateTime, nullable=False)
    
    # Additional metrics for comprehensive analysis
    sentiment_score = Column(Float, default=0.0)  # Sentiment analysis score (-1 to 1)
    virality_score = Column(Float, default=0.0)   # Rate of engagement growth
    relevance_score = Column(Float, default=0.0)  # Keyword relevance score
    
    # Relationships
    post = relationship("Post", back_populates="metrics")
    
    # Indexes for performance
    __table_args__ = (
        Index('ix_metrics_post_calculated', 'post_id', 'calculated_at'),
        Index('ix_metrics_engagement_score', 'engagement_score'),
        Index('ix_metrics_tfidf_score', 'tfidf_score'),
        Index('ix_metrics_trend_velocity', 'trend_velocity'),
    )

    def __repr__(self):
        return f"<Metric(id={self.id}, post_id={self.post_id}, engagement={self.engagement_score:.2f}, tfidf={self.tfidf_score:.2f})>"