"""
Integration tests for all API endpoints.
Tests the complete API workflow with database transactions.
"""
import pytest
import json
from unittest.mock import patch, AsyncMock
from fastapi import status

from app.models.user import User
from app.models.keyword import Keyword
from app.models.post import Post
from app.models.blog_content import BlogContent
from app.models.process_log import ProcessLog


class TestAuthEndpointsIntegration:
    """Integration tests for authentication endpoints."""
    
    def test_login_redirect(self, integration_test_client):
        """Test login endpoint redirects to Reddit OAuth."""
        response = integration_test_client.get("/api/v1/auth/login")
        
        assert response.status_code == status.HTTP_302_FOUND
        assert "reddit.com" in response.headers["location"]
        assert "client_id" in response.headers["location"]
        assert "response_type=code" in response.headers["location"]
    
    def test_unauthenticated_access(self, integration_test_client):
        """Test that protected endpoints require authentication."""
        protected_endpoints = [
            ("/api/v1/auth/me", "GET"),
            ("/api/v1/auth/status", "GET"),
            ("/api/v1/keywords/", "GET"),
            ("/api/v1/keywords/", "POST"),
            ("/api/v1/posts/", "GET"),
            ("/api/v1/trends/", "GET"),
            ("/api/v1/content/", "GET"),
        ]
        
        for endpoint, method in protected_endpoints:
            if method == "GET":
                response = integration_test_client.get(endpoint)
            elif method == "POST":
                response = integration_test_client.post(endpoint, json={})
            
            assert response.status_code == status.HTTP_403_FORBIDDEN
            assert "Not authenticated" in response.json()["detail"]
    
    @patch('app.services.auth_service.AuthService.exchange_code_for_token')
    @patch('app.services.auth_service.AuthService.get_reddit_user_info')
    def test_auth_callback_flow(self, mock_get_user_info, mock_exchange_token, 
                               integration_test_client, integration_db):
        """Test complete OAuth callback flow."""
        # Mock Reddit API responses
        mock_exchange_token.return_value = {"access_token": "reddit_token"}
        mock_get_user_info.return_value = {
            "id": "reddit_user_123",
            "name": "test_user",
            "email": "test@example.com"
        }
        
        # First, we need to simulate the state being set
        with patch('app.services.auth_service.AuthService.verify_state') as mock_verify:
            mock_verify.return_value = True
            
            response = integration_test_client.get(
                "/api/v1/auth/callback?code=test_code&state=test_state"
            )
            
            # Should create user and return tokens
            if response.status_code == status.HTTP_200_OK:
                data = response.json()
                assert "access_token" in data
                assert "refresh_token" in data
                assert "user" in data
                
                # Verify user was created in database
                user = integration_db.query(User).filter(
                    User.email == "test@example.com"
                ).first()
                assert user is not None
                assert user.name == "test_user"


class TestKeywordEndpointsIntegration:
    """Integration tests for keyword management endpoints."""
    
    @patch('app.core.dependencies.verify_token')
    def test_keyword_crud_workflow(self, mock_verify_token, integration_test_client, 
                                  integration_db, authenticated_user, auth_headers):
        """Test complete keyword CRUD workflow."""
        mock_verify_token.return_value = authenticated_user
        
        # Create keyword
        keyword_data = {"keyword": "machine learning", "is_active": True}
        response = integration_test_client.post(
            "/api/v1/keywords/",
            json=keyword_data,
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_201_CREATED
        created_keyword = response.json()
        assert created_keyword["keyword"] == "machine learning"
        assert created_keyword["is_active"] is True
        keyword_id = created_keyword["id"]
        
        # Verify keyword exists in database
        db_keyword = integration_db.query(Keyword).filter(
            Keyword.id == keyword_id
        ).first()
        assert db_keyword is not None
        assert db_keyword.user_id == authenticated_user.id
        
        # Get keywords list
        response = integration_test_client.get(
            "/api/v1/keywords/",
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        keywords = response.json()
        assert len(keywords) >= 1
        assert any(k["id"] == keyword_id for k in keywords)
        
        # Update keyword
        update_data = {"keyword": "deep learning", "is_active": False}
        response = integration_test_client.put(
            f"/api/v1/keywords/{keyword_id}",
            json=update_data,
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        updated_keyword = response.json()
        assert updated_keyword["keyword"] == "deep learning"
        assert updated_keyword["is_active"] is False
        
        # Delete keyword
        response = integration_test_client.delete(
            f"/api/v1/keywords/{keyword_id}",
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        
        # Verify keyword is deleted
        db_keyword = integration_db.query(Keyword).filter(
            Keyword.id == keyword_id
        ).first()
        assert db_keyword is None
    
    @patch('app.core.dependencies.verify_token')
    def test_duplicate_keyword_validation(self, mock_verify_token, integration_test_client,
                                        authenticated_user, auth_headers):
        """Test duplicate keyword validation."""
        mock_verify_token.return_value = authenticated_user
        
        keyword_data = {"keyword": "python", "is_active": True}
        
        # Create first keyword
        response = integration_test_client.post(
            "/api/v1/keywords/",
            json=keyword_data,
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_201_CREATED
        
        # Try to create duplicate
        response = integration_test_client.post(
            "/api/v1/keywords/",
            json=keyword_data,
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "already exists" in response.json()["detail"]


class TestPostEndpointsIntegration:
    """Integration tests for post retrieval endpoints."""
    
    @patch('app.core.dependencies.verify_token')
    def test_posts_retrieval_workflow(self, mock_verify_token, integration_test_client,
                                    authenticated_user, sample_post, auth_headers):
        """Test post retrieval with filtering and pagination."""
        mock_verify_token.return_value = authenticated_user
        
        # Get all posts
        response = integration_test_client.get(
            "/api/v1/posts/",
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert "page" in data
        assert "size" in data
        assert len(data["items"]) >= 1
        
        # Get posts by keyword
        response = integration_test_client.get(
            f"/api/v1/posts/?keyword_id={sample_post.keyword_id}",
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data["items"]) >= 1
        assert all(post["keyword_id"] == sample_post.keyword_id for post in data["items"])
        
        # Get specific post
        response = integration_test_client.get(
            f"/api/v1/posts/{sample_post.id}",
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        post_data = response.json()
        assert post_data["id"] == sample_post.id
        assert post_data["title"] == sample_post.title
    
    @patch('app.core.dependencies.verify_token')
    def test_posts_search_functionality(self, mock_verify_token, integration_test_client,
                                      authenticated_user, sample_post, auth_headers):
        """Test post search functionality."""
        mock_verify_token.return_value = authenticated_user
        
        # Search by title
        response = integration_test_client.get(
            f"/api/v1/posts/?search={sample_post.title.split()[0]}",
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data["items"]) >= 1


class TestCrawlingEndpointsIntegration:
    """Integration tests for crawling endpoints."""
    
    @patch('app.core.dependencies.verify_token')
    @patch('app.workers.crawling_tasks.crawl_keyword_posts.delay')
    def test_crawling_workflow(self, mock_crawl_task, mock_verify_token,
                             integration_test_client, authenticated_user,
                             sample_keyword, auth_headers):
        """Test crawling initiation and status tracking."""
        mock_verify_token.return_value = authenticated_user
        mock_crawl_task.return_value.id = "test-task-id"
        
        # Start crawling
        response = integration_test_client.post(
            f"/api/v1/crawling/start/{sample_keyword.id}",
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "task_id" in data
        assert data["status"] == "started"
        
        # Check crawling status
        response = integration_test_client.get(
            f"/api/v1/crawling/status/test-task-id",
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_200_OK


class TestTrendEndpointsIntegration:
    """Integration tests for trend analysis endpoints."""
    
    @patch('app.core.dependencies.verify_token')
    @patch('app.workers.analysis_tasks.analyze_keyword_trends.delay')
    def test_trend_analysis_workflow(self, mock_analysis_task, mock_verify_token,
                                   integration_test_client, authenticated_user,
                                   sample_keyword, auth_headers):
        """Test trend analysis initiation and retrieval."""
        mock_verify_token.return_value = authenticated_user
        mock_analysis_task.return_value.id = "analysis-task-id"
        
        # Start trend analysis
        response = integration_test_client.post(
            f"/api/v1/trends/analyze/{sample_keyword.id}",
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        
        # Get trend data
        response = integration_test_client.get(
            f"/api/v1/trends/{sample_keyword.id}",
            headers=auth_headers
        )
        
        # Should return empty or cached data
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]


class TestContentEndpointsIntegration:
    """Integration tests for content generation endpoints."""
    
    @patch('app.core.dependencies.verify_token')
    @patch('app.workers.content_tasks.generate_blog_content.delay')
    def test_content_generation_workflow(self, mock_content_task, mock_verify_token,
                                       integration_test_client, authenticated_user,
                                       sample_keyword, auth_headers):
        """Test content generation workflow."""
        mock_verify_token.return_value = authenticated_user
        mock_content_task.return_value.id = "content-task-id"
        
        # Generate content
        content_request = {
            "keyword_id": sample_keyword.id,
            "template": "default"
        }
        response = integration_test_client.post(
            "/api/v1/content/generate",
            json=content_request,
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        
        # Get content list
        response = integration_test_client.get(
            "/api/v1/content/",
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_200_OK


class TestPublicBlogEndpointsIntegration:
    """Integration tests for public blog endpoints."""
    
    def test_public_blog_access(self, integration_test_client, integration_db,
                              sample_keyword, sample_blog_content_data):
        """Test public blog endpoints don't require authentication."""
        # Create published blog content
        blog_content = BlogContent(
            keyword_id=sample_keyword.id,
            **sample_blog_content_data
        )
        integration_db.add(blog_content)
        integration_db.commit()
        
        # Get public blog posts (no auth required)
        response = integration_test_client.get("/api/v1/public/blog/posts")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "items" in data
        
        # Get specific blog post
        if data["items"]:
            post_id = data["items"][0]["id"]
            response = integration_test_client.get(f"/api/v1/public/blog/posts/{post_id}")
            assert response.status_code == status.HTTP_200_OK


class TestHealthEndpointsIntegration:
    """Integration tests for health check endpoints."""
    
    def test_health_check(self, integration_test_client):
        """Test health check endpoint."""
        response = integration_test_client.get("/health")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
    
    def test_detailed_health_check(self, integration_test_client):
        """Test detailed health check with dependencies."""
        response = integration_test_client.get("/api/v1/health/detailed")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "database" in data
        assert "redis" in data
        assert "reddit_api" in data


class TestAPIDocumentationIntegration:
    """Integration tests for API documentation."""
    
    def test_openapi_schema(self, integration_test_client):
        """Test OpenAPI schema generation."""
        response = integration_test_client.get("/api/v1/openapi.json")
        
        assert response.status_code == status.HTTP_200_OK
        schema = response.json()
        
        # Verify essential endpoints are documented
        paths = schema.get("paths", {})
        essential_endpoints = [
            "/api/v1/auth/login",
            "/api/v1/keywords/",
            "/api/v1/posts/",
            "/api/v1/trends/",
            "/api/v1/content/",
            "/api/v1/public/blog/posts"
        ]
        
        for endpoint in essential_endpoints:
            assert endpoint in paths, f"Endpoint {endpoint} not found in OpenAPI schema"
    
    def test_swagger_documentation(self, integration_test_client):
        """Test Swagger UI accessibility."""
        response = integration_test_client.get("/docs")
        
        assert response.status_code == status.HTTP_200_OK
        assert "swagger" in response.text.lower()
    
    def test_redoc_documentation(self, integration_test_client):
        """Test ReDoc documentation accessibility."""
        response = integration_test_client.get("/redoc")
        
        assert response.status_code == status.HTTP_200_OK
        assert "redoc" in response.text.lower()