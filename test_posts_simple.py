"""
Simple test for posts API functionality.
"""

import pytest
from datetime import datetime, timedelta
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.core.database import get_db, Base
from app.models.user import User
from app.models.keyword import Keyword
from app.models.post import Post, Comment
from app.core.security import create_access_token


# Create test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_posts.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Override database dependency for testing."""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="module")
def setup_database():
    """Set up test database."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


@pytest.fixture
def db_session():
    """Create database session."""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def test_user(db_session, setup_database):
    """Create test user."""
    user = User(
        name="Test User",
        email="test@example.com",
        oauth_provider="google",
        oauth_id="test_oauth_id_123"
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def test_keyword(db_session, test_user):
    """Create test keyword."""
    keyword = Keyword(
        user_id=test_user.id,
        keyword="python",
        is_active=True
    )
    db_session.add(keyword)
    db_session.commit()
    db_session.refresh(keyword)
    return keyword


@pytest.fixture
def test_posts(db_session, test_keyword):
    """Create test posts."""
    posts = []
    for i in range(3):
        post = Post(
            keyword_id=test_keyword.id,
            reddit_id=f"test_post_{i}",
            title=f"Test Post {i}",
            content=f"This is test post content {i}",
            author=f"author_{i}",
            score=i * 10,
            num_comments=i * 2,
            url=f"https://reddit.com/r/test/post_{i}",
            subreddit="test",
            post_created_at=datetime.utcnow() - timedelta(days=i)
        )
        db_session.add(post)
        posts.append(post)
    
    db_session.commit()
    for post in posts:
        db_session.refresh(post)
    
    return posts


@pytest.fixture
def auth_headers(test_user):
    """Create authentication headers."""
    token = create_access_token(data={"sub": str(test_user.id)})
    return {"Authorization": f"Bearer {token}"}


def test_get_posts_list(client, test_posts, auth_headers):
    """Test getting posts list."""
    response = client.get("/api/v1/posts/", headers=auth_headers)
    assert response.status_code == 200
    
    data = response.json()
    assert "posts" in data
    assert "total" in data
    assert data["total"] == 3
    assert len(data["posts"]) == 3


def test_get_posts_with_pagination(client, test_posts, auth_headers):
    """Test posts pagination."""
    response = client.get("/api/v1/posts/?page=1&per_page=2", headers=auth_headers)
    assert response.status_code == 200
    
    data = response.json()
    assert data["total"] == 3
    assert len(data["posts"]) == 2
    assert data["page"] == 1
    assert data["per_page"] == 2
    assert data["has_next"] is True
    assert data["has_prev"] is False


def test_get_post_detail(client, test_posts, auth_headers):
    """Test getting post detail."""
    post_id = test_posts[0].id
    response = client.get(f"/api/v1/posts/{post_id}", headers=auth_headers)
    assert response.status_code == 200
    
    data = response.json()
    assert data["id"] == post_id
    assert "comments" in data


def test_get_posts_by_keyword(client, test_keyword, test_posts, auth_headers):
    """Test getting posts by keyword."""
    response = client.get(f"/api/v1/posts/keyword/{test_keyword.id}", headers=auth_headers)
    assert response.status_code == 200
    
    data = response.json()
    assert data["total"] == 3
    assert len(data["posts"]) == 3


def test_search_posts(client, test_posts, auth_headers):
    """Test searching posts."""
    response = client.get("/api/v1/posts/search/query?q=Test Post 1", headers=auth_headers)
    assert response.status_code == 200
    
    data = response.json()
    assert data["total"] == 1
    assert "Test Post 1" in data["posts"][0]["title"]


def test_get_post_statistics(client, test_posts, auth_headers):
    """Test getting post statistics."""
    response = client.get("/api/v1/posts/stats/summary", headers=auth_headers)
    assert response.status_code == 200
    
    data = response.json()
    assert "statistics" in data
    stats = data["statistics"]
    assert stats["total_posts"] == 3


def test_unauthorized_access(client):
    """Test unauthorized access."""
    response = client.get("/api/v1/posts/")
    assert response.status_code == 401


def test_post_not_found(client, auth_headers):
    """Test accessing non-existent post."""
    response = client.get("/api/v1/posts/999", headers=auth_headers)
    assert response.status_code == 404


if __name__ == "__main__":
    pytest.main([__file__, "-v"])