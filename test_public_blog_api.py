"""
Test public blog API endpoints.
"""

import pytest
from datetime import datetime
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.core.database import get_db, Base
from app.models.user import User
from app.models.keyword import Keyword
from app.models.blog_content import BlogContent

# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_public_blog.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="function")
def setup_database():
    """Create tables and clean up after each test."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)

@pytest.fixture
def test_data(setup_database):
    """Create test data."""
    db = TestingSessionLocal()
    
    # Create test user
    user = User(
        name="Test User",
        email="test@example.com",
        oauth_provider="reddit",
        oauth_id="test_oauth_id_123",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Create test keywords
    keyword1 = Keyword(
        user_id=user.id,
        keyword="technology",
        is_active=True,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    keyword2 = Keyword(
        user_id=user.id,
        keyword="programming",
        is_active=True,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db.add_all([keyword1, keyword2])
    db.commit()
    db.refresh(keyword1)
    db.refresh(keyword2)
    
    # Create test blog content
    blog_posts = [
        BlogContent(
            keyword_id=keyword1.id,
            title="The Future of Technology",
            content="# The Future of Technology\n\nTechnology is evolving rapidly. Here are some key trends to watch...",
            template_used="default",
            generated_at=datetime.utcnow(),
            word_count=150,
            status="published",
            slug="future-of-technology",
            meta_description="Exploring the latest technology trends and innovations",
            tags="technology,innovation,future",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        ),
        BlogContent(
            keyword_id=keyword2.id,
            title="Best Programming Practices",
            content="# Best Programming Practices\n\nWriting clean code is essential. Here are some best practices...",
            template_used="default",
            generated_at=datetime.utcnow(),
            word_count=200,
            status="published",
            slug="best-programming-practices",
            meta_description="Learn the best practices for writing clean, maintainable code",
            tags="programming,coding,best-practices",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        ),
        BlogContent(
            keyword_id=keyword1.id,
            title="Draft Post",
            content="# Draft Post\n\nThis is a draft post that should not appear in public API.",
            template_used="default",
            generated_at=datetime.utcnow(),
            word_count=50,
            status="draft",
            slug="draft-post",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
    ]
    
    db.add_all(blog_posts)
    db.commit()
    
    db.close()
    return {
        "user": user,
        "keywords": [keyword1, keyword2],
        "published_posts": blog_posts[:2],
        "draft_post": blog_posts[2]
    }

def test_list_blog_posts(client, test_data):
    """Test listing published blog posts."""
    response = client.get("/api/v1/blog/posts")
    assert response.status_code == 200
    
    data = response.json()
    assert data["total"] == 2  # Only published posts
    assert len(data["posts"]) == 2
    assert data["page"] == 1
    assert data["size"] == 10
    assert data["has_next"] is False
    assert data["has_prev"] is False
    
    # Check post data
    post = data["posts"][0]
    assert "id" in post
    assert "title" in post
    assert "slug" in post
    assert "excerpt" in post
    assert "tags" in post
    assert "published_at" in post

def test_list_blog_posts_with_pagination(client, test_data):
    """Test blog posts pagination."""
    response = client.get("/api/v1/blog/posts?page=1&size=1")
    assert response.status_code == 200
    
    data = response.json()
    assert data["total"] == 2
    assert len(data["posts"]) == 1
    assert data["pages"] == 2
    assert data["has_next"] is True
    assert data["has_prev"] is False

def test_list_blog_posts_with_category_filter(client, test_data):
    """Test filtering posts by category."""
    response = client.get("/api/v1/blog/posts?category=technology")
    assert response.status_code == 200
    
    data = response.json()
    assert data["total"] == 1
    assert len(data["posts"]) == 1
    assert "technology" in data["posts"][0]["title"].lower()

def test_list_blog_posts_with_tag_filter(client, test_data):
    """Test filtering posts by tag."""
    response = client.get("/api/v1/blog/posts?tag=programming")
    assert response.status_code == 200
    
    data = response.json()
    assert data["total"] == 1
    assert len(data["posts"]) == 1
    assert "programming" in data["posts"][0]["tags"]

def test_get_blog_post_by_slug(client, test_data):
    """Test getting a specific blog post by slug."""
    response = client.get("/api/v1/blog/posts/future-of-technology")
    assert response.status_code == 200
    
    data = response.json()
    assert data["title"] == "The Future of Technology"
    assert data["slug"] == "future-of-technology"
    assert "content" in data
    assert data["word_count"] == 150
    assert data["estimated_read_time"] == 1

def test_get_blog_post_by_slug_not_found(client, test_data):
    """Test getting non-existent blog post."""
    response = client.get("/api/v1/blog/posts/non-existent-post")
    assert response.status_code == 404

def test_get_blog_post_draft_not_accessible(client, test_data):
    """Test that draft posts are not accessible via public API."""
    response = client.get("/api/v1/blog/posts/draft-post")
    assert response.status_code == 404

def test_list_blog_categories(client, test_data):
    """Test listing blog categories."""
    response = client.get("/api/v1/blog/categories")
    assert response.status_code == 200
    
    data = response.json()
    assert len(data) == 2
    
    # Check category structure
    category = data[0]
    assert "name" in category
    assert "slug" in category
    assert "count" in category
    assert category["count"] > 0

def test_list_blog_tags(client, test_data):
    """Test listing blog tags."""
    response = client.get("/api/v1/blog/tags")
    assert response.status_code == 200
    
    data = response.json()
    assert len(data) > 0
    
    # Check tag structure
    tag = data[0]
    assert "name" in tag
    assert "slug" in tag
    assert "count" in tag
    assert tag["count"] > 0

def test_search_blog_posts(client, test_data):
    """Test searching blog posts."""
    response = client.get("/api/v1/blog/search?q=technology")
    assert response.status_code == 200
    
    data = response.json()
    assert data["total"] >= 1
    assert data["query"] == "technology"
    assert "search_time_ms" in data
    assert len(data["posts"]) >= 1

def test_search_blog_posts_no_results(client, test_data):
    """Test searching with no results."""
    response = client.get("/api/v1/blog/search?q=nonexistent")
    assert response.status_code == 200
    
    data = response.json()
    assert data["total"] == 0
    assert len(data["posts"]) == 0

def test_get_blog_stats(client, test_data):
    """Test getting blog statistics."""
    response = client.get("/api/v1/blog/stats")
    assert response.status_code == 200
    
    data = response.json()
    assert data["total_posts"] == 2
    assert data["total_words"] == 350  # 150 + 200
    assert data["total_tags"] > 0
    assert "latest_post_date" in data
    assert data["average_read_time"] >= 1

def test_get_related_posts(client, test_data):
    """Test getting related posts."""
    # First get a post ID
    response = client.get("/api/v1/blog/posts")
    posts = response.json()["posts"]
    post_id = posts[0]["id"]
    
    response = client.get(f"/api/v1/blog/posts/{post_id}/related")
    assert response.status_code == 200
    
    data = response.json()
    # Should return related posts (may be empty if no similar posts)
    assert isinstance(data, list)
    
    if data:  # If there are related posts
        related_post = data[0]
        assert "id" in related_post
        assert "title" in related_post
        assert "similarity_score" in related_post

def test_get_related_posts_not_found(client, test_data):
    """Test getting related posts for non-existent post."""
    response = client.get("/api/v1/blog/posts/999/related")
    assert response.status_code == 404

def test_get_rss_feed(client, test_data):
    """Test generating RSS feed."""
    response = client.get("/api/v1/blog/rss")
    assert response.status_code == 200
    
    data = response.json()
    assert data["title"] == "Reddit Trends Blog"
    assert "items" in data
    assert len(data["items"]) == 2  # Published posts only
    
    if data["items"]:
        item = data["items"][0]
        assert "title" in item
        assert "link" in item
        assert "description" in item
        assert "pub_date" in item

def test_get_sitemap(client, test_data):
    """Test generating sitemap."""
    response = client.get("/api/v1/blog/sitemap")
    assert response.status_code == 200
    
    data = response.json()
    assert "urls" in data
    assert len(data["urls"]) >= 4  # Homepage, posts index, + 2 posts
    
    url = data["urls"][0]
    assert "loc" in url
    assert "lastmod" in url
    assert "changefreq" in url
    assert "priority" in url

def test_get_blog_archive(client, test_data):
    """Test getting blog archive for current month."""
    now = datetime.utcnow()
    response = client.get(f"/api/v1/blog/archive/{now.year}/{now.month}")
    assert response.status_code == 200
    
    data = response.json()
    assert data["year"] == now.year
    assert data["month"] == now.month
    assert data["count"] >= 0
    assert "posts" in data

def test_api_endpoints_no_auth_required(client, test_data):
    """Test that public blog endpoints don't require authentication."""
    endpoints = [
        "/api/v1/blog/posts",
        "/api/v1/blog/categories",
        "/api/v1/blog/tags",
        "/api/v1/blog/stats",
        "/api/v1/blog/rss",
        "/api/v1/blog/sitemap"
    ]
    
    for endpoint in endpoints:
        response = client.get(endpoint)
        # Should not return 401 or 403 (authentication/authorization errors)
        assert response.status_code not in [401, 403]

if __name__ == "__main__":
    pytest.main([__file__, "-v"])