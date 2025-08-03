"""
Simplified integration tests that work with existing fixtures.
"""
import pytest
from datetime import datetime, timezone
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock, MagicMock

from app.main import app
from app.models.user import User
from app.models.keyword import Keyword
from app.models.post import Post


@pytest.fixture
def test_client():
    """Create a test client for the FastAPI app."""
    return TestClient(app)


class TestAPIIntegration:
    """Basic API integration tests."""
    
    def test_health_endpoint(self, test_client):
        """Test health endpoint is accessible."""
        response = test_client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
    
    def test_openapi_schema(self, test_client):
        """Test OpenAPI schema is accessible."""
        response = test_client.get("/api/v1/openapi.json")
        assert response.status_code == 200
        schema = response.json()
        assert "paths" in schema
        assert "info" in schema
    
    def test_swagger_docs(self, test_client):
        """Test Swagger documentation is accessible."""
        response = test_client.get("/docs")
        assert response.status_code == 200
        assert "swagger" in response.text.lower()
    
    def test_redoc_docs(self, test_client):
        """Test ReDoc documentation is accessible."""
        response = test_client.get("/redoc")
        assert response.status_code == 200
        assert "redoc" in response.text.lower()


class TestAuthenticationIntegration:
    """Authentication integration tests."""
    
    def test_login_redirect(self, test_client):
        """Test login endpoint redirects to Reddit OAuth."""
        response = test_client.get("/api/v1/auth/login")
        assert response.status_code == 302
        assert "reddit.com" in response.headers["location"]
    
    def test_protected_endpoints_require_auth(self, test_client):
        """Test that protected endpoints require authentication."""
        protected_endpoints = [
            "/api/v1/auth/me",
            "/api/v1/auth/status",
            "/api/v1/keywords/",
            "/api/v1/posts/",
        ]
        
        for endpoint in protected_endpoints:
            response = test_client.get(endpoint)
            assert response.status_code == 403
            assert "Not authenticated" in response.json()["detail"]


class TestDatabaseIntegration:
    """Database integration tests."""
    
    def test_user_model_structure(self):
        """Test user model structure."""
        user = User(
            name="Test User",
            email="test@example.com",
            oauth_provider="reddit"
        )
        
        assert user.name == "Test User"
        assert user.email == "test@example.com"
        assert user.oauth_provider == "reddit"
    
    def test_keyword_model_structure(self, sample_user):
        """Test keyword model structure."""
        keyword = Keyword(
            user_id=sample_user.id,
            keyword="test keyword",
            is_active=True
        )
        
        assert keyword.user_id == sample_user.id
        assert keyword.keyword == "test keyword"
        assert keyword.is_active is True
    
    def test_post_model_structure(self, sample_keyword):
        """Test post model structure."""
        post = Post(
            keyword_id=sample_keyword.id,
            reddit_id="test_post_123",
            title="Test Post",
            content="Test content",
            author="test_author",
            score=100,
            num_comments=10,
            url="https://reddit.com/test",
            subreddit="test"
        )
        
        assert post.keyword_id == sample_keyword.id
        assert post.reddit_id == "test_post_123"
        assert post.title == "Test Post"


class TestRedditServiceIntegration:
    """Reddit service integration tests."""
    
    def test_reddit_service_imports(self):
        """Test that Reddit service components can be imported."""
        from app.services.reddit_service import RedditPostData, RedditCommentData
        
        # Test data structures
        post_data = RedditPostData(
            reddit_id="test_123",
            title="Test Post",
            content="Test content",
            author="test_author",
            score=100,
            num_comments=20,
            url="https://reddit.com/test",
            subreddit="test",
            created_at=datetime.now()
        )
        
        assert post_data.reddit_id == "test_123"
        assert post_data.title == "Test Post"
        
        comment_data = RedditCommentData(
            reddit_id="comment_123",
            body="Test comment",
            author="commenter",
            score=10
        )
        
        assert comment_data.reddit_id == "comment_123"
        assert comment_data.body == "Test comment"


class TestCeleryTasksIntegration:
    """Celery tasks integration tests."""
    
    def test_crawl_keyword_posts_task_import(self):
        """Test keyword posts crawling task import."""
        from app.workers.crawling_tasks import crawl_keyword_posts
        
        # Test that the task can be imported and called
        assert callable(crawl_keyword_posts)
    
    def test_celery_task_imports(self):
        """Test that Celery tasks can be imported."""
        # Test crawling tasks
        from app.workers.crawling_tasks import (
            crawl_keyword_posts, 
            crawl_subreddit_posts
        )
        
        assert callable(crawl_keyword_posts)
        assert callable(crawl_subreddit_posts)
        
        # Test analysis tasks
        from app.workers.analysis_tasks import (
            analyze_keyword_trends_task,
            calculate_post_metrics_task
        )
        
        assert callable(analyze_keyword_trends_task)
        assert callable(calculate_post_metrics_task)
        
        # Test content tasks
        from app.workers.content_tasks import (
            generate_blog_content_task,
            process_content_template_task
        )
        
        assert callable(generate_blog_content_task)
        assert callable(process_content_template_task)


class TestExternalAPIMocking:
    """External API mocking integration tests."""
    
    def test_auth_service_import(self):
        """Test that auth service can be imported."""
        from app.services.auth_service import AuthService
        
        auth_service = AuthService()
        
        # Test auth URL generation
        auth_url = auth_service.get_reddit_auth_url("test_state")
        
        assert "reddit.com" in auth_url
        assert "client_id" in auth_url
        assert "test_state" in auth_url
    
    @patch('httpx.AsyncClient.get')
    @pytest.mark.asyncio
    async def test_oauth_user_info(self, mock_get):
        """Test OAuth user info retrieval with mocking."""
        # Mock user info response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "id": "reddit_user_123",
            "name": "test_user",
            "created": 1640995200,
            "has_verified_email": True
        }
        mock_get.return_value = mock_response
        
        from app.services.auth_service import AuthService
        auth_service = AuthService()
        
        user_info = await auth_service.get_reddit_user_info("mock_access_token")
        
        assert user_info["id"] == "reddit_user_123"
        assert user_info["name"] == "test_user"


class TestWorkflowIntegration:
    """End-to-end workflow integration tests."""
    
    def test_service_imports(self):
        """Test that all services can be imported."""
        from app.services.auth_service import AuthService
        from app.services.keyword_service import KeywordService
        from app.services.post_service import PostService
        from app.services.trend_analysis_service import TrendAnalysisService
        from app.services.content_generation_service import ContentGenerationService
        
        # Test service instantiation
        auth_service = AuthService()
        keyword_service = KeywordService()
        post_service = PostService()
        trend_service = TrendAnalysisService()
        content_service = ContentGenerationService()
        
        assert auth_service is not None
        assert keyword_service is not None
        assert post_service is not None
        assert trend_service is not None
        assert content_service is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])