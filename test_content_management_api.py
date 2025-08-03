"""
Test content management API endpoints.
"""

import pytest
from datetime import datetime
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from unittest.mock import patch, MagicMock

from app.main import app
from app.core.database import get_db, Base
from app.models.user import User
from app.models.keyword import Keyword
from app.models.blog_content import BlogContent
from app.core.security import create_access_token

# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_content_api.db"
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
def test_user(setup_database):
    """Create test user."""
    db = TestingSessionLocal()
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
    db.close()
    return user

@pytest.fixture
def test_keyword(test_user, setup_database):
    """Create test keyword."""
    db = TestingSessionLocal()
    keyword = Keyword(
        user_id=test_user.id,
        keyword="test_keyword",
        is_active=True,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db.add(keyword)
    db.commit()
    db.refresh(keyword)
    db.close()
    return keyword

@pytest.fixture
def test_blog_content(test_keyword, setup_database):
    """Create test blog content."""
    db = TestingSessionLocal()
    content = BlogContent(
        keyword_id=test_keyword.id,
        title="Test Blog Post",
        content="# Test Content\n\nThis is test content.",
        template_used="default",
        generated_at=datetime.utcnow(),
        word_count=5,
        status="draft",
        slug="test-blog-post",
        meta_description="Test meta description",
        tags="test,blog,content",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db.add(content)
    db.commit()
    db.refresh(content)
    db.close()
    return content

@pytest.fixture
def auth_headers(test_user):
    """Create authentication headers."""
    token = create_access_token(subject=str(test_user.id))
    return {"Authorization": f"Bearer {token}"}

def test_list_content_empty(setup_database, client, auth_headers):
    """Test listing content when no content exists."""
    response = client.get("/api/v1/content/", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["items"] == []
    assert data["total"] == 0
    assert data["page"] == 1
    assert data["size"] == 20

def test_list_content_with_data(setup_database, client, auth_headers, test_blog_content):
    """Test listing content with existing data."""
    response = client.get("/api/v1/content/", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 1
    assert data["total"] == 1
    assert data["items"][0]["title"] == "Test Blog Post"
    assert data["items"][0]["status"] == "draft"

def test_list_content_pagination(setup_database, client, auth_headers, test_keyword):
    """Test content listing with pagination."""
    # Create multiple blog contents
    db = TestingSessionLocal()
    for i in range(5):
        content = BlogContent(
            keyword_id=test_keyword.id,
            title=f"Test Blog Post {i}",
            content=f"# Test Content {i}\n\nThis is test content {i}.",
            template_used="default",
            generated_at=datetime.utcnow(),
            word_count=5,
            status="draft",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.add(content)
    db.commit()
    db.close()
    
    # Test pagination
    response = client.get("/api/v1/content/?page=1&size=3", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 3
    assert data["total"] == 5
    assert data["pages"] == 2

def test_list_content_filter_by_keyword(setup_database, client, auth_headers, test_user):
    """Test filtering content by keyword."""
    db = TestingSessionLocal()
    
    # Create two keywords
    keyword1 = Keyword(user_id=test_user.id, keyword="keyword1", is_active=True, created_at=datetime.utcnow(), updated_at=datetime.utcnow())
    keyword2 = Keyword(user_id=test_user.id, keyword="keyword2", is_active=True, created_at=datetime.utcnow(), updated_at=datetime.utcnow())
    db.add_all([keyword1, keyword2])
    db.commit()
    db.refresh(keyword1)
    db.refresh(keyword2)
    
    # Create content for each keyword
    content1 = BlogContent(keyword_id=keyword1.id, title="Content 1", content="Content", template_used="default", generated_at=datetime.utcnow(), word_count=1, status="draft", created_at=datetime.utcnow(), updated_at=datetime.utcnow())
    content2 = BlogContent(keyword_id=keyword2.id, title="Content 2", content="Content", template_used="default", generated_at=datetime.utcnow(), word_count=1, status="draft", created_at=datetime.utcnow(), updated_at=datetime.utcnow())
    db.add_all([content1, content2])
    db.commit()
    db.close()
    
    # Test filtering
    response = client.get(f"/api/v1/content/?keyword_id={keyword1.id}", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 1
    assert data["items"][0]["title"] == "Content 1"

def test_get_content_by_id(setup_database, client, auth_headers, test_blog_content):
    """Test getting specific content by ID."""
    response = client.get(f"/api/v1/content/{test_blog_content.id}", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == test_blog_content.id
    assert data["title"] == "Test Blog Post"
    assert data["content"] == "# Test Content\n\nThis is test content."
    assert data["status"] == "draft"

def test_get_content_not_found(setup_database, client, auth_headers):
    """Test getting non-existent content."""
    response = client.get("/api/v1/content/999", headers=auth_headers)
    assert response.status_code == 404
    assert "Content not found" in response.json()["detail"]

def test_update_content(setup_database, client, auth_headers, test_blog_content):
    """Test updating blog content."""
    update_data = {
        "title": "Updated Blog Post",
        "content": "# Updated Content\n\nThis is updated content.",
        "status": "published",
        "tags": ["updated", "test"]
    }
    
    response = client.put(f"/api/v1/content/{test_blog_content.id}", json=update_data, headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated Blog Post"
    assert data["content"] == "# Updated Content\n\nThis is updated content."
    assert data["status"] == "published"

def test_update_content_not_found(setup_database, client, auth_headers):
    """Test updating non-existent content."""
    update_data = {"title": "Updated Title"}
    response = client.put("/api/v1/content/999", json=update_data, headers=auth_headers)
    assert response.status_code == 404

def test_delete_content(setup_database, client, auth_headers, test_blog_content):
    """Test deleting blog content."""
    response = client.delete(f"/api/v1/content/{test_blog_content.id}", headers=auth_headers)
    assert response.status_code == 200
    assert "deleted successfully" in response.json()["message"]
    
    # Verify content is deleted
    response = client.get(f"/api/v1/content/{test_blog_content.id}", headers=auth_headers)
    assert response.status_code == 404

def test_delete_content_not_found(setup_database, client, auth_headers):
    """Test deleting non-existent content."""
    response = client.delete("/api/v1/content/999", headers=auth_headers)
    assert response.status_code == 404

@patch('app.workers.content_tasks.generate_blog_content_task.delay')
def test_generate_content(mock_task, setup_database, client, auth_headers, test_keyword):
    """Test content generation endpoint."""
    mock_task.return_value = MagicMock(id="test-task-id")
    
    request_data = {
        "keyword_id": test_keyword.id,
        "template_type": "default",
        "include_trends": True,
        "include_top_posts": True,
        "max_posts": 10
    }
    
    response = client.post("/api/v1/content/generate", json=request_data, headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["task_id"] == "test-task-id"
    assert data["status"] == "pending"
    assert "generation started" in data["message"]

def test_generate_content_invalid_keyword(setup_database, client, auth_headers):
    """Test content generation with invalid keyword."""
    request_data = {
        "keyword_id": 999,
        "template_type": "default"
    }
    
    response = client.post("/api/v1/content/generate", json=request_data, headers=auth_headers)
    assert response.status_code == 404
    assert "Keyword not found" in response.json()["detail"]

@patch('app.workers.content_tasks.batch_generate_content_task.delay')
def test_batch_generate_content(mock_task, setup_database, client, auth_headers, test_user):
    """Test batch content generation."""
    mock_task.return_value = MagicMock(id="batch-task-id")
    
    # Create multiple keywords
    db = TestingSessionLocal()
    keyword1 = Keyword(user_id=test_user.id, keyword="keyword1", is_active=True, created_at=datetime.utcnow(), updated_at=datetime.utcnow())
    keyword2 = Keyword(user_id=test_user.id, keyword="keyword2", is_active=True, created_at=datetime.utcnow(), updated_at=datetime.utcnow())
    db.add_all([keyword1, keyword2])
    db.commit()
    db.refresh(keyword1)
    db.refresh(keyword2)
    db.close()
    
    response = client.post(
        "/api/v1/content/batch-generate",
        json={"keyword_ids": [keyword1.id, keyword2.id]},
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["task_id"] == "batch-task-id"
    assert "2 keywords" in data["message"]

@patch('app.services.task_service.TaskService.get_task_status')
def test_get_generation_status(mock_get_status, setup_database, client, auth_headers):
    """Test getting content generation status."""
    mock_get_status.return_value = {
        "status": "completed",
        "progress": 100,
        "message": "Content generated successfully",
        "result": {"content_id": 1},
        "error": None,
        "created_at": datetime.utcnow(),
        "completed_at": datetime.utcnow()
    }
    
    response = client.get("/api/v1/content/generation-status/test-task-id", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["task_id"] == "test-task-id"
    assert data["status"] == "completed"
    assert data["progress"] == 100

@patch('app.services.content_generation_service.ContentGenerationService.preview_content')
def test_preview_content(mock_preview, setup_database, client, auth_headers, test_keyword):
    """Test content preview generation."""
    mock_preview.return_value = {
        "title": "Preview Title",
        "content_preview": "This is a preview...",
        "word_count": 100,
        "estimated_read_time": 1,
        "tags": ["preview", "test"],
        "template_used": "default"
    }
    
    request_data = {
        "keyword_id": test_keyword.id,
        "template_type": "default"
    }
    
    response = client.post("/api/v1/content/preview", json=request_data, headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Preview Title"
    assert data["word_count"] == 100

@patch('app.workers.content_tasks.regenerate_content_task.delay')
def test_regenerate_content(mock_task, setup_database, client, auth_headers, test_blog_content):
    """Test content regeneration."""
    mock_task.return_value = MagicMock(id="regen-task-id")
    
    response = client.post(
        f"/api/v1/content/{test_blog_content.id}/regenerate",
        json={"template_type": "listicle"},
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["task_id"] == "regen-task-id"
    assert "regeneration started" in data["message"]

@patch('app.services.template_service.TemplateService.get_available_templates')
def test_list_templates(mock_templates, setup_database, client):
    """Test listing available templates."""
    mock_templates.return_value = [
        {
            "name": "default",
            "description": "Default blog template",
            "variables": ["keyword", "trend_data", "top_posts"]
        },
        {
            "name": "listicle",
            "description": "List-style blog template",
            "variables": ["keyword", "top_posts", "insights"]
        }
    ]
    
    response = client.get("/api/v1/content/templates/")
    assert response.status_code == 200
    data = response.json()
    assert len(data["templates"]) == 2
    assert data["templates"][0]["name"] == "default"
    assert data["templates"][1]["name"] == "listicle"

def test_unauthorized_access(setup_database, client):
    """Test accessing endpoints without authentication."""
    response = client.get("/api/v1/content/")
    assert response.status_code == 403
    
    response = client.get("/api/v1/content/1")
    assert response.status_code == 403
    
    response = client.post("/api/v1/content/generate", json={"keyword_id": 1})
    assert response.status_code == 403

if __name__ == "__main__":
    pytest.main([__file__, "-v"])