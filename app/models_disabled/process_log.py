"""
Process log model for tracking background tasks and operations.
"""

from sqlalchemy import Column, String, Integer, ForeignKey, Text, DateTime, Index
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


class ProcessLog(BaseModel):
    """
    ProcessLog model for tracking background tasks and operations.
    Provides audit trail and status monitoring for async operations.
    """
    __tablename__ = "process_logs"

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    task_type = Column(String(100), nullable=False)  # crawling, analysis, content_generation, deployment
    status = Column(String(50), nullable=False, default="pending")  # pending, running, completed, failed, cancelled
    task_id = Column(String(255), nullable=False)  # Celery task ID
    error_message = Column(Text)  # Error details if failed
    completed_at = Column(DateTime)  # When task completed
    
    # Additional tracking fields
    progress_percentage = Column(Integer, default=0)  # 0-100
    items_processed = Column(Integer, default=0)
    total_items = Column(Integer, default=0)
    
    # Task-specific metadata (JSON)
    task_metadata = Column(Text)  # JSON string with task-specific data
    
    # Performance metrics
    execution_time_seconds = Column(Integer)  # Total execution time
    memory_usage_mb = Column(Integer)  # Peak memory usage
    
    # Relationships
    user = relationship("User", back_populates="process_logs")
    
    # Indexes for performance
    __table_args__ = (
        Index('ix_process_logs_user_task_type', 'user_id', 'task_type'),
        Index('ix_process_logs_status', 'status'),
        Index('ix_process_logs_task_id', 'task_id'),
        Index('ix_process_logs_created_at', 'created_at'),
    )

    def __repr__(self):
        return f"<ProcessLog(id={self.id}, user_id={self.user_id}, task_type='{self.task_type}', status='{self.status}')>"