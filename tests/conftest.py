"""
Test configuration and fixtures for unit tests.
"""
import asyncio
import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import Base, get_db
from app.core.config import Settings
from app.models.user import User
from app.models.keyword import Keyword
from app.models.post import Post
from app.models.blog_content import BlogContent


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def test_settings():
    """Test settings configuration."""
    return Settings(
        DATABASE_URL="sqlite:///:memory:",
        REDIS_URL="redis://localhost:6379/1",
        JWT_SECRET_KEY="test-secret-key",
        JWT_ALGORITHM="HS256",
        JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30,
        REDDIT_CLIENT_ID="test-client-id",
        REDDIT_CLIENT_SECRET="test-client-secret"
    )


@pytest.fixture
def test_db_engine():
    """Create test database engine."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    return engine


@pytest.fixture
def test_db_session(test_db_engine):
    """Create test database session."""
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_db_engine)
    session = TestingSessionLocal()
    
    # Mock the session for unit tests
    session.query = MagicMock()
    session.add = MagicMock()
    session.commit = MagicMock()
    session.delete = MagicMock()
    session.refresh = MagicMock()
    
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def mock_redis():
    """Mock Redis client."""
    redis_mock = MagicMock()
    redis_mock.get = AsyncMock(return_value=None)
    redis_mock.set = AsyncMock(return_value=True)
    redis_mock.delete = AsyncMock(return_value=True)
    redis_mock.exists = AsyncMock(return_value=False)
    redis_mock.expire = AsyncMock(return_value=True)
    return redis_mock


@pytest.fixture
def sample_user():
    """Sample user for testing."""
    return User(
        id=1,
        name="Test User",
        email="test@example.com",
        oauth_provider="reddit"
    )


@pytest.fixture
def sample_keyword(sample_user):
    """Sample keyword for testing."""
    return Keyword(
        id=1,
        user_id=sample_user.id,
        keyword="python",
        is_active=True
    )


@pytest.fixture
def sample_post(sample_keyword):
    """Sample post for testing."""
    return Post(
        id=1,
        keyword_id=sample_keyword.id,
        reddit_id="test_post_id",
        title="Test Post Title",
        content="This is a test post content",
        author="test_author",
        score=100,
        num_comments=25,
        url="https://reddit.com/r/test/comments/test_post_id"
    )


@pytest.fixture
def sample_blog_content(sample_keyword):
    """Sample blog content for testing."""
    return BlogContent(
        id=1,
        keyword_id=sample_keyword.id,
        title="Test Blog Post",
        content="# Test Blog Post\n\nThis is test content.",
        template_used="default",
        status="published"
    )


@pytest.fixture
def mock_reddit_api():
    """Mock Reddit API responses."""
    mock_api = MagicMock()
    
    # Mock subreddit search
    mock_submission = MagicMock()
    mock_submission.id = "test_post_id"
    mock_submission.title = "Test Post Title"
    mock_submission.selftext = "Test post content"
    mock_submission.author.name = "test_author"
    mock_submission.score = 100
    mock_submission.num_comments = 25
    mock_submission.url = "https://reddit.com/r/test/comments/test_post_id"
    mock_submission.created_utc = 1640995200  # 2022-01-01
    
    mock_api.subreddit.return_value.search.return_value = [mock_submission]
    
    # Mock comments
    mock_comment = MagicMock()
    mock_comment.id = "test_comment_id"
    mock_comment.body = "Test comment"
    mock_comment.author.name = "test_commenter"
    mock_comment.score = 10
    mock_comment.created_utc = 1640995200
    
    mock_submission.comments.list.return_value = [mock_comment]
    
    return mock_api


@pytest.fixture
def mock_celery_task():
    """Mock Celery task."""
    task_mock = MagicMock()
    task_mock.id = "test-task-id"
    task_mock.state = "PENDING"
    task_mock.result = None
    return task_mock