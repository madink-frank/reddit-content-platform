"""
Application configuration settings using Pydantic Settings.
Handles environment variables and provides type-safe configuration.
"""

from typing import List, Optional, Union
from pydantic import AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings
import os


class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    # Project Information
    PROJECT_NAME: str = "Reddit Content Platform"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Database Configuration
    DATABASE_URL: str = "sqlite:///./reddit_platform.db"
    
    # Redis Configuration
    REDIS_URL: str = "redis://localhost:6379"
    
    # Supabase Configuration
    SUPABASE_URL: Optional[str] = None
    SUPABASE_ANON_KEY: Optional[str] = None
    SUPABASE_SERVICE_ROLE_KEY: Optional[str] = None
    
    # JWT Configuration
    JWT_SECRET_KEY: str = "demo-secret-key-for-local-development-only"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # CORS Configuration
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = [
        "http://localhost:3000",  # React dev server
        "http://localhost:8080",  # Alternative frontend port
        "http://localhost:5173",  # Vite dev server
    ]
    
    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)
    
    # Reddit API Configuration
    REDDIT_CLIENT_ID: str = "demo_client_id"
    REDDIT_CLIENT_SECRET: str = "demo_client_secret"
    REDDIT_REDIRECT_URI: str = "http://localhost:8000/api/v1/auth/callback"
    REDDIT_USER_AGENT: str = "RedditContentPlatform/1.0"
    
    # Celery Configuration
    CELERY_BROKER_URL: str = "redis://localhost:6379"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379"
    
    # Alternative RabbitMQ configuration (uncomment to use RabbitMQ instead of Redis)
    # CELERY_BROKER_URL: str = "pyamqp://guest@localhost//"
    # CELERY_RESULT_BACKEND: str = "rpc://"
    
    # Notification Configuration (Optional)
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: int = 587
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    ADMIN_EMAIL: Optional[str] = None
    
    # Webhook Configuration (Optional)
    WEBHOOK_URL: Optional[str] = None
    
    # Environment
    ENVIRONMENT: str = "development"
    
    # Logging Configuration
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"  # json or text
    LOG_REQUEST_DETAILS: bool = False  # Log detailed request/response info
    LOG_SQL_QUERIES: bool = False  # Log SQL queries (debug only)
    SLOW_QUERY_THRESHOLD_MS: float = 100.0  # Threshold for slow query logging
    LOG_CORRELATION_ID_HEADER: str = "X-Correlation-ID"  # Header for correlation ID
    LOG_MAX_STRING_LENGTH: int = 1000  # Maximum length for logged strings
    LOG_EXCLUDE_PATHS: List[str] = ["/health", "/metrics"]  # Paths to exclude from request logging
    
    # Alert Configuration
    ALERT_WEBHOOK_URL: Optional[str] = None
    ALERT_EMAIL_ENABLED: bool = False
    ALERT_SLACK_WEBHOOK: Optional[str] = None
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    
    # Reddit API Rate Limiting
    REDDIT_REQUESTS_PER_MINUTE: int = 60
    REDDIT_REQUESTS_PER_SECOND: int = 1
    
    # Content Generation Settings
    MAX_POSTS_PER_KEYWORD: int = 100
    CONTENT_GENERATION_TIMEOUT: int = 300  # seconds
    
    # Deployment Settings
    VERCEL_TOKEN: Optional[str] = None
    NETLIFY_TOKEN: Optional[str] = None
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()