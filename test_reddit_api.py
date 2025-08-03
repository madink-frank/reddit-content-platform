"""
Test Reddit API endpoints.
"""

import pytest
from unittest.mock import patch, Mock
from fastapi.testclient import TestClient
from datetime import datetime, timezone

from app.main import app
from app.services.reddit_service import RedditPostData, RedditCommentData


client = TestClient(app)


class TestRedditAPI:
    """Test Reddit API endpoints."""
    
    def test_reddit_health_check(self):
        """Test Reddit health check endpoint."""
        with patch('app.services.reddit_service.reddit_client.health_check') as mock_health:
            mock_health.return_value = {
                "status": "healthy",
                "message": "Reddit API connection is working",
                "timestamp": "2022-01-01T00:00:00"
            }
            
            response = client.get("/api/v1/reddit/health")
            
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "healthy"
            assert "Reddit API connection is working" in data["message"]
    
    def test_reddit_health_check_failure(self):
        """Test Reddit health check endpoint when service is down."""
        with patch('app.services.reddit_service.reddit_client.health_check') as mock_health:
            mock_health.side_effect = Exception("Connection failed")
            
            response = client.get("/api/v1/reddit/health")
            
            assert response.status_code == 503
            data = response.json()
            assert "Reddit API health check failed" in data["detail"]
    
    def test_search_reddit_posts_unauthorized(self):
        """Test searching Reddit posts without authentication."""
        response = client.get("/api/v1/reddit/search?keyword=python")
        
        assert response.status_code == 401
    
    def test_search_reddit_posts_authorized(self):
        """Test searching Reddit posts with authentication."""
        # Mock authentication
        with patch('app.core.dependencies.get_current_user') as mock_auth:
            mock_user = Mock()
            mock_user.id = 1
            mock_user.name = "test_user"
            mock_auth.return_value = mock_user
            
            # Mock Reddit service
            with patch('app.services.reddit_service.reddit_client.search_posts_by_keyword') as mock_search:
                mock_post = RedditPostData(
                    reddit_id="test123",
                    title="Test Post",
                    content="Test content",
                    author="test_author",
                    score=100,
                    num_comments=25,
                    url="https://reddit.com/test",
                    subreddit="test",
                    created_at=datetime.now(timezone.utc)
                )
                mock_search.return_value = [mock_post]
                
                response = client.get("/api/v1/reddit/search?keyword=python&limit=5")
                
                assert response.status_code == 200
                data = response.json()
                assert len(data) == 1
                assert data[0]["reddit_id"] == "test123"
                assert data[0]["title"] == "Test Post"
                assert data[0]["author"] == "test_author"
                assert data[0]["score"] == 100
    
    def test_get_reddit_post_comments_authorized(self):
        """Test getting Reddit post comments with authentication."""
        # Mock authentication
        with patch('app.core.dependencies.get_current_user') as mock_auth:
            mock_user = Mock()
            mock_user.id = 1
            mock_user.name = "test_user"
            mock_auth.return_value = mock_user
            
            # Mock Reddit service
            with patch('app.services.reddit_service.reddit_client.get_post_comments') as mock_comments:
                mock_comment = RedditCommentData(
                    reddit_id="comment123",
                    body="Test comment",
                    author="comment_author",
                    score=10,
                    created_at=datetime.now(timezone.utc)
                )
                mock_comments.return_value = [mock_comment]
                
                response = client.get("/api/v1/reddit/posts/test123/comments?limit=10")
                
                assert response.status_code == 200
                data = response.json()
                assert len(data) == 1
                assert data[0]["reddit_id"] == "comment123"
                assert data[0]["body"] == "Test comment"
                assert data[0]["author"] == "comment_author"
                assert data[0]["score"] == 10
    
    def test_get_subreddit_posts_authorized(self):
        """Test getting subreddit posts with authentication."""
        # Mock authentication
        with patch('app.core.dependencies.get_current_user') as mock_auth:
            mock_user = Mock()
            mock_user.id = 1
            mock_user.name = "test_user"
            mock_auth.return_value = mock_user
            
            # Mock Reddit service
            with patch('app.services.reddit_service.reddit_client.get_subreddit_posts') as mock_posts:
                mock_post = RedditPostData(
                    reddit_id="subreddit123",
                    title="Subreddit Post",
                    content="Subreddit content",
                    author="subreddit_author",
                    score=200,
                    num_comments=50,
                    url="https://reddit.com/r/python/test",
                    subreddit="python",
                    created_at=datetime.now(timezone.utc)
                )
                mock_posts.return_value = [mock_post]
                
                response = client.get("/api/v1/reddit/subreddit/python?limit=5&sort=hot")
                
                assert response.status_code == 200
                data = response.json()
                assert len(data) == 1
                assert data[0]["reddit_id"] == "subreddit123"
                assert data[0]["title"] == "Subreddit Post"
                assert data[0]["subreddit"] == "python"
                assert data[0]["score"] == 200
    
    def test_search_posts_error_handling(self):
        """Test error handling in search posts endpoint."""
        # Mock authentication
        with patch('app.core.dependencies.get_current_user') as mock_auth:
            mock_user = Mock()
            mock_user.id = 1
            mock_auth.return_value = mock_user
            
            # Mock Reddit service error
            with patch('app.services.reddit_service.reddit_client.search_posts_by_keyword') as mock_search:
                mock_search.side_effect = Exception("Reddit API Error")
                
                response = client.get("/api/v1/reddit/search?keyword=python")
                
                assert response.status_code == 500
                data = response.json()
                assert "Failed to search Reddit posts" in data["detail"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])