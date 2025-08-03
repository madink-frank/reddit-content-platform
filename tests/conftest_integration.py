"""
Integration test configuration and fixtures.
"""
import asyncio
import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from unittest.mock import AsyncMock, MagicMock, patch
import redis
from celery import Celery

from app.main import app
from app.core.database import Base, get_db
from app.core.config import Settings
from app.core.redis_client import get_redis_client
from app.core.celery_app import celery_app
from app.models.user import User
from app.models.keyword import Keyword
from app.models.post import Post
from app.models.blog_content import BlogContent
from app.models.metric import Metric
from app.models.process_log import ProcessLog


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def integration_settings():
    """Integration test settings configuration."""
    return Settings(
        DATABASE_URL="sqlite:///./test_integration.db",
        REDIS_URL="redis://localhost:6379/15",  # Use test database
        JWT_SECRET_KEY="integration-test-secret-key",
        JWT_ALGORITHM="HS256",
        JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30,
        REDDIT_CLIENT_ID="test-client-id",
        REDDIT_CLIENT_SECRET="test-client-secret",
        CELERY_BROKER_URL="redis://localhost:6379/14",
        CELERY_RESULT_BACKEND="redis://localhost:6379/14"
    )


@pytest.fixture(scope="session")
def integration_db_engine(integration_settings):
    """Create integration test database engine."""
    engine = create_engine(
        integration_settings.DATABASE_URL,
        connect_args={"check_same_thread": False}
    )
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="session")
def integration_db_session(integration_db_engine):
    """Create integration test database session."""
    TestingSessionLocal = sessionmaker(
        autocommit=False, 
        autoflush=False, 
        bind=integration_db_engine
    )
    return TestingSessionLocal


@pytest.fixture
def integration_db(integration_db_session):
    """Create a fresh database session for each test."""
    session = integration_db_session()
    try:
        yield session
    finally:
        session.rollback()
        session.close()


@pytest.fixture(scope="session")
def integration_redis_client(integration_settings):
    """Create integration test Redis client."""
    redis_client = redis.from_url(integration_settings.REDIS_URL)
    yield redis_client
    # Clean up test data
    redis_client.flushdb()
    redis_client.close()


@pytest.fixture
def integration_test_client(integration_db_session, integration_redis_client):
    """Create FastAPI test client with database and Redis overrides."""
    
    def override_get_db():
        session = integration_db_session()
        try:
            yield session
        finally:
            session.close()
    
    def override_get_redis():
        return integration_redis_client
    
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_redis_client] = override_get_redis
    
    with TestClient(app) as client:
        yield client
    
    # Clean up overrides
    app.dependency_overrides.clear()


@pytest.fixture
def integration_celery_app(integration_settings):
    """Create Celery app for integration testing."""
    test_celery = Celery(
        "test_app",
        broker=integration_settings.CELERY_BROKER_URL,
        backend=integration_settings.CELERY_RESULT_BACKEND
    )
    test_celery.conf.update(
        task_always_eager=True,  # Execute tasks synchronously
        task_eager_propagates=True,  # Propagate exceptions
        result_expires=3600,
    )
    return test_celery


@pytest.fixture
def sample_user_data():
    """Sample user data for integration tests."""
    return {
        "name": "Integration Test User",
        "email": "integration@test.com",
        "oauth_provider": "reddit"
    }


@pytest.fixture
def sample_keyword_data():
    """Sample keyword data for integration tests."""
    return {
        "keyword": "python programming",
        "is_active": True
    }


@pytest.fixture
def sample_post_data():
    """Sample post data for integration tests."""
    return {
        "reddit_id": "integration_post_123",
        "title": "Integration Test Post",
        "content": "This is a test post for integration testing",
        "author": "test_author",
        "score": 150,
        "num_comments": 25,
        "url": "https://reddit.com/r/test/comments/integration_post_123",
        "subreddit": "test"
    }


@pytest.fixture
def sample_blog_content_data():
    """Sample blog content data for integration tests."""
    return {
        "title": "Integration Test Blog Post",
        "content": "# Integration Test\n\nThis is a test blog post.",
        "template_used": "default",
        "status": "published"
    }


@pytest.fixture
def mock_reddit_api():
    """Mock Reddit API for integration tests."""
    with patch('app.services.reddit_service.reddit_client') as mock_client:
        # Mock search results
        mock_submission = MagicMock()
        mock_submission.id = "test_post_123"
        mock_submission.title = "Test Post Title"
        mock_submission.selftext = "Test post content"
        mock_submission.author.__str__ = MagicMock(return_value="test_author")
        mock_submission.score = 100
        mock_submission.num_comments = 25
        mock_submission.url = "https://reddit.com/r/test/comments/test_post_123"
        mock_submission.subreddit.__str__ = MagicMock(return_value="test")
        mock_submission.created_utc = 1640995200
        
        mock_client.search_posts_by_keyword = AsyncMock(return_value=[
            {
                "reddit_id": "test_post_123",
                "title": "Test Post Title",
                "content": "Test post content",
                "author": "test_author",
                "score": 100,
                "num_comments": 25,
                "url": "https://reddit.com/r/test/comments/test_post_123",
                "subreddit": "test",
                "created_at": "2022-01-01T00:00:00Z"
            }
        ])
        
        mock_client.get_post_comments = AsyncMock(return_value=[
            {
                "reddit_id": "test_comment_123",
                "body": "Test comment",
                "author": "test_commenter",
                "score": 10,
                "created_at": "2022-01-01T00:10:00Z"
            }
        ])
        
        mock_client.health_check = AsyncMock(return_value={
            "status": "healthy",
            "message": "Reddit API connection is working"
        })
        
        yield mock_client


@pytest.fixture
def auth_headers():
    """Generate authentication headers for testing."""
    # This would normally create a real JWT token
    # For integration tests, we'll mock the authentication
    return {"Authorization": "Bearer test_integration_token"}


@pytest.fixture
def authenticated_user(integration_db, sample_user_data):
    """Create an authenticated user in the database."""
    user = User(**sample_user_data)
    integration_db.add(user)
    integration_db.commit()
    integration_db.refresh(user)
    return user


@pytest.fixture
def sample_keyword(integration_db, authenticated_user, sample_keyword_data):
    """Create a sample keyword in the database."""
    keyword = Keyword(
        user_id=authenticated_user.id,
        **sample_keyword_data
    )
    integration_db.add(keyword)
    integration_db.commit()
    integration_db.refresh(keyword)
    return keyword


@pytest.fixture
def sample_post(integration_db, sample_keyword, sample_post_data):
    """Create a sample post in the database."""
    post = Post(
        keyword_id=sample_keyword.id,
        **sample_post_data
    )
    integration_db.add(post)
    integration_db.commit()
    integration_db.refresh(post)
    return post