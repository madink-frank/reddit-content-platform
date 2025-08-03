"""
Test posts API endpoints.
"""

import pytest
from datetime import datetime, timedelta
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.main import app
from app.core.database import get_db
from app.models.user import User
from app.models.keyword import Keyword
from app.models.post import Post, Comment
from app.core.security import create_access_token


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


@pytest.fixture
def test_db():
    """Create test database session."""
    from app.core.database import engine, Base
    from sqlalchemy.orm import sessionmaker
    
    # Create test database
    Base.metadata.create_all(bind=engine)
    
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = TestingSessionLocal()
    
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def test_user(test_db: Session):
    """Create test user."""
    user = User(
        name="Test User",
        email="test@example.com",
        oauth_provider="google",
        oauth_id="test_oauth_id_123"
    )
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)
    return user


@pytest.fixture
def test_keyword(test_db: Session, test_user: User):
    """Create test keyword."""
    keyword = Keyword(
        user_id=test_user.id,
        keyword="python",
        is_active=True
    )
    test_db.add(keyword)
    test_db.commit()
    test_db.refresh(keyword)
    return keyword


@pytest.fixture
def test_posts(test_db: Session, test_keyword: Keyword):
    """Create test posts."""
    posts = []
    for i in range(5):
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
        test_db.add(post)
        posts.append(post)
    
    test_db.commit()
    for post in posts:
        test_db.refresh(post)
    
    return posts


@pytest.fixture
def test_comments(test_db: Session, test_posts):
    """Create test comments."""
    comments = []
    for i, post in enumerate(test_posts[:2]):  # Add comments to first 2 posts
        for j in range(3):
            comment = Comment(
                post_id=post.id,
                reddit_id=f"comment_{i}_{j}",
                body=f"Test comment {j} for post {i}",
                author=f"commenter_{j}",
                score=j * 5,
                comment_created_at=datetime.utcnow() - timedelta(hours=j)
            )
            test_db.add(comment)
            comments.append(comment)
    
    test_db.commit()
    for comment in comments:
        test_db.refresh(comment)
    
    return comments


@pytest.fixture
def auth_headers(test_user: User):
    """Create authentication headers."""
    token = create_access_token(data={"sub": str(test_user.id)})
    return {"Authorization": f"Bearer {token}"}


def override_get_db(test_db: Session):
    """Override database dependency."""
    def _override():
        try:
            yield test_db
        finally:
            pass
    return _override


def test_get_posts_list(client: TestClient, test_db: Session, test_user: User, test_posts, auth_headers):
    """Test getting posts list."""
    # Override database dependency
    app.dependency_overrides[get_db] = override_get_db(test_db)
    
    try:
        response = client.get("/api/v1/posts/", headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        assert "posts" in data
        assert "total" in data
        assert "page" in data
        assert "per_page" in data
        assert data["total"] == 5
        assert len(data["posts"]) == 5
        
        # Check first post
        first_post = data["posts"][0]
        assert "id" in first_post
        assert "title" in first_post
        assert "content" in first_post
        assert "author" in first_post
        assert "score" in first_post
        
    finally:
        app.dependency_overrides.clear()


def test_get_posts_with_pagination(client: TestClient, test_db: Session, test_user: User, test_posts, auth_headers):
    """Test posts pagination."""
    app.dependency_overrides[get_db] = override_get_db(test_db)
    
    try:
        # Get first page with 2 items per page
        response = client.get("/api/v1/posts/?page=1&per_page=2", headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        assert data["total"] == 5
        assert len(data["posts"]) == 2
        assert data["page"] == 1
        assert data["per_page"] == 2
        assert data["total_pages"] == 3
        assert data["has_next"] is True
        assert data["has_prev"] is False
        
        # Get second page
        response = client.get("/api/v1/posts/?page=2&per_page=2", headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        assert len(data["posts"]) == 2
        assert data["page"] == 2
        assert data["has_next"] is True
        assert data["has_prev"] is True
        
    finally:
        app.dependency_overrides.clear()


def test_get_post_detail(client: TestClient, test_db: Session, test_user: User, test_posts, test_comments, auth_headers):
    """Test getting post detail with comments."""
    app.dependency_overrides[get_db] = override_get_db(test_db)
    
    try:
        post_id = test_posts[0].id
        response = client.get(f"/api/v1/posts/{post_id}", headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        assert data["id"] == post_id
        assert "comments" in data
        assert len(data["comments"]) == 3  # 3 comments for first post
        
        # Check comment structure
        comment = data["comments"][0]
        assert "id" in comment
        assert "body" in comment
        assert "author" in comment
        assert "score" in comment
        
    finally:
        app.dependency_overrides.clear()


def test_get_posts_by_keyword(client: TestClient, test_db: Session, test_user: User, test_keyword: Keyword, test_posts, auth_headers):
    """Test getting posts by keyword."""
    app.dependency_overrides[get_db] = override_get_db(test_db)
    
    try:
        response = client.get(f"/api/v1/posts/keyword/{test_keyword.id}", headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        assert data["total"] == 5
        assert len(data["posts"]) == 5
        
        # All posts should belong to the keyword
        for post in data["posts"]:
            assert post["keyword_id"] == test_keyword.id
            
    finally:
        app.dependency_overrides.clear()


def test_search_posts(client: TestClient, test_db: Session, test_user: User, test_posts, auth_headers):
    """Test searching posts."""
    app.dependency_overrides[get_db] = override_get_db(test_db)
    
    try:
        # Search for "Test Post 1"
        response = client.get("/api/v1/posts/search/query?q=Test Post 1", headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        assert data["total"] == 1
        assert len(data["posts"]) == 1
        assert "Test Post 1" in data["posts"][0]["title"]
        
    finally:
        app.dependency_overrides.clear()


def test_get_posts_with_filters(client: TestClient, test_db: Session, test_user: User, test_posts, auth_headers):
    """Test posts filtering."""
    app.dependency_overrides[get_db] = override_get_db(test_db)
    
    try:
        # Filter by minimum score
        response = client.get("/api/v1/posts/?min_score=20", headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        assert data["total"] == 3  # Posts with score >= 20 (20, 30, 40)
        
        # Filter by author
        response = client.get("/api/v1/posts/?author=author_1", headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        assert data["total"] == 1
        assert data["posts"][0]["author"] == "author_1"
        
    finally:
        app.dependency_overrides.clear()


def test_get_posts_with_sorting(client: TestClient, test_db: Session, test_user: User, test_posts, auth_headers):
    """Test posts sorting."""
    app.dependency_overrides[get_db] = override_get_db(test_db)
    
    try:
        # Sort by score ascending
        response = client.get("/api/v1/posts/?sort_by=score&sort_order=asc", headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        scores = [post["score"] for post in data["posts"]]
        assert scores == sorted(scores)  # Should be in ascending order
        
        # Sort by score descending
        response = client.get("/api/v1/posts/?sort_by=score&sort_order=desc", headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        scores = [post["score"] for post in data["posts"]]
        assert scores == sorted(scores, reverse=True)  # Should be in descending order
        
    finally:
        app.dependency_overrides.clear()


def test_get_post_statistics(client: TestClient, test_db: Session, test_user: User, test_posts, auth_headers):
    """Test getting post statistics."""
    app.dependency_overrides[get_db] = override_get_db(test_db)
    
    try:
        response = client.get("/api/v1/posts/stats/summary", headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        assert "user_id" in data
        assert "statistics" in data
        
        stats = data["statistics"]
        assert stats["total_posts"] == 5
        assert stats["average_score"] == 20.0  # (0+10+20+30+40)/5
        assert stats["total_comments"] == 10  # 0+2+4+6+8
        assert stats["unique_subreddits"] == 1  # All posts in "test" subreddit
        
    finally:
        app.dependency_overrides.clear()


def test_unauthorized_access(client: TestClient):
    """Test unauthorized access to posts endpoints."""
    # No auth headers
    response = client.get("/api/v1/posts/")
    assert response.status_code == 401
    
    response = client.get("/api/v1/posts/1")
    assert response.status_code == 401
    
    response = client.get("/api/v1/posts/keyword/1")
    assert response.status_code == 401
    
    response = client.get("/api/v1/posts/search/query?q=test")
    assert response.status_code == 401


def test_post_not_found(client: TestClient, test_db: Session, test_user: User, auth_headers):
    """Test accessing non-existent post."""
    app.dependency_overrides[get_db] = override_get_db(test_db)
    
    try:
        response = client.get("/api/v1/posts/999", headers=auth_headers)
        assert response.status_code == 404
        
    finally:
        app.dependency_overrides.clear()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])