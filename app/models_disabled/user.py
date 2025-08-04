"""
User model for authentication and user management.
"""

from sqlalchemy import Column, String, DateTime
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


class User(BaseModel):
    """
    User model for OAuth2 authentication.
    Stores user information from OAuth providers.
    """
    __tablename__ = "users"

    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    oauth_provider = Column(String(50), nullable=False)  # reddit, google, github, etc.
    oauth_id = Column(String(255), nullable=False)  # OAuth provider user ID
    oauth_id = Column(String(255), nullable=False)  # OAuth provider user ID
    
    # Relationships
    keywords = relationship("Keyword", back_populates="user", cascade="all, delete-orphan")
    process_logs = relationship("ProcessLog", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}', provider='{self.oauth_provider}')>"