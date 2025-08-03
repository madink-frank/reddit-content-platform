"""
Integration tests for external API mocking and service interactions.
"""
import pytest
from unittest.mock import patch, AsyncMock, MagicMock
import httpx
import json
from datetime import datetime, timezone

from app.services.reddit_service import RedditService
from app.services.auth_service import AuthService
from app.core.config import Settings


class TestRedditAPIMocking:
    """Integration tests for Reddit API mocking."""
    
    @patch('app.services.reddit_service.praw.Reddit')
    def test_reddit_api_authentication_mock(self, mock_reddit_class):
        """Test Reddit API authentication with mocking."""
        # Mock Reddit instance
        mock_reddit_instance = MagicMock()
        mock_reddit_class.return_value = mock_reddit_instance
        
        # Mock user authentication
        mock_reddit_instance.auth.url.return_value = "https://reddit.com/api/v1/authorize?client_id=test"
        
        # Create Reddit service
        reddit_service = RedditService()
        
        # Test authentication URL generation
        auth_url = reddit_service.get_auth_url("test_state")
        
        assert "reddit.com" in auth_url
        assert "client_id" in auth_url
        assert "test_state" in auth_url
    
    @patch('app.services.reddit_service.praw.Reddit')
    @pytest.mark.asyncio
    async def test_reddit_search_posts_mock(self, mock_reddit_class):
        """Test Reddit post search with comprehensive mocking."""
        # Mock Reddit instance and subreddit
        mock_reddit_instance = MagicMock()
        mock_subreddit = MagicMock()
        mock_reddit_class.return_value = mock_reddit_instance
        mock_reddit_instance.subreddit.return_value = mock_subreddit
        
        # Mock search results
        mock_submission1 = MagicMock()
        mock_submission1.id = "post1"
        mock_submission1.title = "Python Tutorial"
        mock_submission1.selftext = "Learn Python programming"
        mock_submission1.author.name = "python_teacher"
        mock_submission1.score = 150
        mock_submission1.num_comments = 25
        mock_submission1.url = "https://reddit.com/r/Python/comments/post1"
        mock_submission1.subreddit.display_name = "Python"
        mock_submission1.created_utc = 1640995200
        
        mock_submission2 = MagicMock()
        mock_submission2.id = "post2"
        mock_submission2.title = "Advanced Python"
        mock_submission2.selftext = "Advanced Python concepts"
        mock_submission2.author.name = "python_expert"
        mock_submission2.score = 200
        mock_submission2.num_comments = 40
        mock_submission2.url = "https://reddit.com/r/Python/comments/post2"
        mock_submission2.subreddit.display_name = "Python"
        mock_submission2.created_utc = 1640998800
        
        mock_subreddit.search.return_value = [mock_submission1, mock_submission2]
        
        # Test search functionality
        reddit_service = RedditService()
        posts = await reddit_service.search_posts_by_keyword("python", limit=10)
        
        assert len(posts) == 2
        assert posts[0]["reddit_id"] == "post1"
        assert posts[0]["title"] == "Python Tutorial"
        assert posts[1]["reddit_id"] == "post2"
        assert posts[1]["title"] == "Advanced Python"
    
    @patch('app.services.reddit_service.praw.Reddit')
    @pytest.mark.asyncio
    async def test_reddit_get_comments_mock(self, mock_reddit_class):
        """Test Reddit comment retrieval with mocking."""
        # Mock Reddit instance
        mock_reddit_instance = MagicMock()
        mock_reddit_class.return_value = mock_reddit_instance
        
        # Mock submission and comments
        mock_submission = MagicMock()
        mock_comment1 = MagicMock()
        mock_comment1.id = "comment1"
        mock_comment1.body = "Great tutorial!"
        mock_comment1.author.name = "student1"
        mock_comment1.score = 15
        mock_comment1.created_utc = 1640995800
        
        mock_comment2 = MagicMock()
        mock_comment2.id = "comment2"
        mock_comment2.body = "Thanks for sharing"
        mock_comment2.author.name = "student2"
        mock_comment2.score = 10
        mock_comment2.created_utc = 1640996400
        
        mock_submission.comments.list.return_value = [mock_comment1, mock_comment2]
        mock_reddit_instance.submission.return_value = mock_submission
        
        # Test comment retrieval
        reddit_service = RedditService()
        comments = await reddit_service.get_post_comments("post1", limit=10)
        
        assert len(comments) == 2
        assert comments[0]["reddit_id"] == "comment1"
        assert comments[0]["body"] == "Great tutorial!"
        assert comments[1]["reddit_id"] == "comment2"
        assert comments[1]["body"] == "Thanks for sharing"
    
    @patch('app.services.reddit_service.praw.Reddit')
    @pytest.mark.asyncio
    async def test_reddit_api_error_handling_mock(self, mock_reddit_class):
        """Test Reddit API error handling with mocking."""
        # Mock Reddit instance that raises exceptions
        mock_reddit_instance = MagicMock()
        mock_subreddit = MagicMock()
        mock_reddit_class.return_value = mock_reddit_instance
        mock_reddit_instance.subreddit.return_value = mock_subreddit
        
        # Mock API error
        from prawcore.exceptions import ResponseException
        mock_subreddit.search.side_effect = ResponseException(
            MagicMock(status_code=429, reason="Too Many Requests")
        )
        
        # Test error handling
        reddit_service = RedditService()
        
        with pytest.raises(Exception) as exc_info:
            await reddit_service.search_posts_by_keyword("python", limit=10)
        
        assert "429" in str(exc_info.value) or "Too Many Requests" in str(exc_info.value)
    
    @patch('app.services.reddit_service.praw.Reddit')
    @pytest.mark.asyncio
    async def test_reddit_rate_limiting_mock(self, mock_reddit_class):
        """Test Reddit API rate limiting with mocking."""
        # Mock Reddit instance
        mock_reddit_instance = MagicMock()
        mock_subreddit = MagicMock()
        mock_reddit_class.return_value = mock_reddit_instance
        mock_reddit_instance.subreddit.return_value = mock_subreddit
        
        # Mock rate limit response
        mock_subreddit.search.return_value = []
        
        # Test multiple rapid requests
        reddit_service = RedditService()
        
        # Make multiple requests
        for i in range(3):
            posts = await reddit_service.search_posts_by_keyword(f"test{i}", limit=5)
            assert isinstance(posts, list)


class TestOAuthAPIMocking:
    """Integration tests for OAuth API mocking."""
    
    @patch('httpx.AsyncClient.post')
    @pytest.mark.asyncio
    async def test_oauth_token_exchange_mock(self, mock_post):
        """Test OAuth token exchange with mocking."""
        # Mock successful token response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "access_token": "mock_access_token",
            "token_type": "bearer",
            "expires_in": 3600,
            "refresh_token": "mock_refresh_token",
            "scope": "identity"
        }
        mock_post.return_value = mock_response
        
        # Test token exchange
        auth_service = AuthService()
        token_data = await auth_service.exchange_code_for_token("test_code", "test_state")
        
        assert token_data["access_token"] == "mock_access_token"
        assert token_data["refresh_token"] == "mock_refresh_token"
        assert token_data["token_type"] == "bearer"
    
    @patch('httpx.AsyncClient.get')
    @pytest.mark.asyncio
    async def test_oauth_user_info_mock(self, mock_get):
        """Test OAuth user info retrieval with mocking."""
        # Mock user info response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "id": "reddit_user_123",
            "name": "test_user",
            "created": 1640995200,
            "link_karma": 1000,
            "comment_karma": 500,
            "has_verified_email": True
        }
        mock_get.return_value = mock_response
        
        # Test user info retrieval
        auth_service = AuthService()
        user_info = await auth_service.get_reddit_user_info("mock_access_token")
        
        assert user_info["id"] == "reddit_user_123"
        assert user_info["name"] == "test_user"
        assert user_info["has_verified_email"] is True
    
    @patch('httpx.AsyncClient.post')
    @pytest.mark.asyncio
    async def test_oauth_token_refresh_mock(self, mock_post):
        """Test OAuth token refresh with mocking."""
        # Mock refresh token response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "access_token": "new_access_token",
            "token_type": "bearer",
            "expires_in": 3600,
            "refresh_token": "new_refresh_token",
            "scope": "identity"
        }
        mock_post.return_value = mock_response
        
        # Test token refresh
        auth_service = AuthService()
        new_token_data = await auth_service.refresh_access_token("old_refresh_token")
        
        assert new_token_data["access_token"] == "new_access_token"
        assert new_token_data["refresh_token"] == "new_refresh_token"
    
    @patch('httpx.AsyncClient.post')
    @pytest.mark.asyncio
    async def test_oauth_error_handling_mock(self, mock_post):
        """Test OAuth error handling with mocking."""
        # Mock error response
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.json.return_value = {
            "error": "invalid_grant",
            "error_description": "The provided authorization grant is invalid"
        }
        mock_post.return_value = mock_response
        
        # Test error handling
        auth_service = AuthService()
        
        with pytest.raises(Exception) as exc_info:
            await auth_service.exchange_code_for_token("invalid_code", "test_state")
        
        assert "invalid_grant" in str(exc_info.value)


class TestExternalServiceIntegration:
    """Integration tests for external service interactions."""
    
    @patch('httpx.AsyncClient')
    @pytest.mark.asyncio
    async def test_external_api_timeout_handling(self, mock_client_class):
        """Test external API timeout handling."""
        # Mock client that times out
        mock_client = MagicMock()
        mock_client_class.return_value.__aenter__.return_value = mock_client
        
        import httpx
        mock_client.get.side_effect = httpx.TimeoutException("Request timed out")
        
        # Test timeout handling
        auth_service = AuthService()
        
        with pytest.raises(Exception) as exc_info:
            await auth_service.get_reddit_user_info("test_token")
        
        assert "timeout" in str(exc_info.value).lower()
    
    @patch('httpx.AsyncClient')
    @pytest.mark.asyncio
    async def test_external_api_connection_error(self, mock_client_class):
        """Test external API connection error handling."""
        # Mock client that has connection issues
        mock_client = MagicMock()
        mock_client_class.return_value.__aenter__.return_value = mock_client
        
        import httpx
        mock_client.post.side_effect = httpx.ConnectError("Connection failed")
        
        # Test connection error handling
        auth_service = AuthService()
        
        with pytest.raises(Exception) as exc_info:
            await auth_service.exchange_code_for_token("test_code", "test_state")
        
        assert "connection" in str(exc_info.value).lower()
    
    @patch('app.services.reddit_service.praw.Reddit')
    @pytest.mark.asyncio
    async def test_reddit_service_health_check_mock(self, mock_reddit_class):
        """Test Reddit service health check with mocking."""
        # Mock healthy Reddit instance
        mock_reddit_instance = MagicMock()
        mock_subreddit = MagicMock()
        mock_reddit_class.return_value = mock_reddit_instance
        mock_reddit_instance.subreddit.return_value = mock_subreddit
        mock_subreddit.display_name = "test"
        
        # Test health check
        reddit_service = RedditService()
        health_status = await reddit_service.health_check()
        
        assert health_status["status"] == "healthy"
        assert "Reddit API connection is working" in health_status["message"]
    
    @patch('app.services.reddit_service.praw.Reddit')
    @pytest.mark.asyncio
    async def test_reddit_service_unhealthy_mock(self, mock_reddit_class):
        """Test Reddit service unhealthy state with mocking."""
        # Mock unhealthy Reddit instance
        mock_reddit_instance = MagicMock()
        mock_reddit_class.return_value = mock_reddit_instance
        mock_reddit_instance.subreddit.side_effect = Exception("API unavailable")
        
        # Test unhealthy state
        reddit_service = RedditService()
        health_status = await reddit_service.health_check()
        
        assert health_status["status"] == "unhealthy"
        assert "error" in health_status


class TestMockDataConsistency:
    """Integration tests for mock data consistency."""
    
    @patch('app.services.reddit_service.praw.Reddit')
    @pytest.mark.asyncio
    async def test_consistent_mock_data_structure(self, mock_reddit_class):
        """Test that mock data maintains consistent structure."""
        # Mock Reddit instance with consistent data
        mock_reddit_instance = MagicMock()
        mock_subreddit = MagicMock()
        mock_reddit_class.return_value = mock_reddit_instance
        mock_reddit_instance.subreddit.return_value = mock_subreddit
        
        # Create consistent mock submissions
        mock_submissions = []
        for i in range(5):
            mock_submission = MagicMock()
            mock_submission.id = f"consistent_post_{i}"
            mock_submission.title = f"Consistent Post {i}"
            mock_submission.selftext = f"Consistent content {i}"
            mock_submission.author.name = f"author_{i}"
            mock_submission.score = 100 + i * 10
            mock_submission.num_comments = 20 + i * 5
            mock_submission.url = f"https://reddit.com/r/test/comments/consistent_post_{i}"
            mock_submission.subreddit.display_name = "test"
            mock_submission.created_utc = 1640995200 + i * 3600
            mock_submissions.append(mock_submission)
        
        mock_subreddit.search.return_value = mock_submissions
        
        # Test data consistency
        reddit_service = RedditService()
        posts = await reddit_service.search_posts_by_keyword("test", limit=10)
        
        assert len(posts) == 5
        
        # Verify all posts have consistent structure
        for i, post in enumerate(posts):
            assert "reddit_id" in post
            assert "title" in post
            assert "content" in post
            assert "author" in post
            assert "score" in post
            assert "num_comments" in post
            assert "url" in post
            assert "subreddit" in post
            assert "created_at" in post
            
            # Verify data consistency
            assert post["reddit_id"] == f"consistent_post_{i}"
            assert post["title"] == f"Consistent Post {i}"
            assert post["author"] == f"author_{i}"
    
    @patch('httpx.AsyncClient')
    @pytest.mark.asyncio
    async def test_oauth_mock_data_consistency(self, mock_client_class):
        """Test OAuth mock data consistency."""
        # Mock consistent OAuth responses
        mock_client = MagicMock()
        mock_client_class.return_value.__aenter__.return_value = mock_client
        
        # Mock token exchange response
        token_response = MagicMock()
        token_response.status_code = 200
        token_response.json.return_value = {
            "access_token": "consistent_access_token",
            "token_type": "bearer",
            "expires_in": 3600,
            "refresh_token": "consistent_refresh_token",
            "scope": "identity"
        }
        
        # Mock user info response
        user_response = MagicMock()
        user_response.status_code = 200
        user_response.json.return_value = {
            "id": "consistent_user_123",
            "name": "consistent_user",
            "created": 1640995200,
            "link_karma": 1000,
            "comment_karma": 500,
            "has_verified_email": True
        }
        
        mock_client.post.return_value = token_response
        mock_client.get.return_value = user_response
        
        # Test consistent OAuth flow
        auth_service = AuthService()
        
        # Exchange code for token
        token_data = await auth_service.exchange_code_for_token("test_code", "test_state")
        assert token_data["access_token"] == "consistent_access_token"
        
        # Get user info
        user_info = await auth_service.get_reddit_user_info(token_data["access_token"])
        assert user_info["id"] == "consistent_user_123"
        assert user_info["name"] == "consistent_user"


class TestMockServiceReliability:
    """Integration tests for mock service reliability."""
    
    @patch('app.services.reddit_service.praw.Reddit')
    @pytest.mark.asyncio
    async def test_mock_service_repeated_calls(self, mock_reddit_class):
        """Test that mock services handle repeated calls consistently."""
        # Mock Reddit instance
        mock_reddit_instance = MagicMock()
        mock_subreddit = MagicMock()
        mock_reddit_class.return_value = mock_reddit_instance
        mock_reddit_instance.subreddit.return_value = mock_subreddit
        
        # Mock consistent responses
        mock_submission = MagicMock()
        mock_submission.id = "reliable_post"
        mock_submission.title = "Reliable Post"
        mock_submission.selftext = "Reliable content"
        mock_submission.author.name = "reliable_author"
        mock_submission.score = 100
        mock_submission.num_comments = 20
        mock_submission.url = "https://reddit.com/r/test/comments/reliable_post"
        mock_submission.subreddit.display_name = "test"
        mock_submission.created_utc = 1640995200
        
        mock_subreddit.search.return_value = [mock_submission]
        
        # Test repeated calls
        reddit_service = RedditService()
        
        for i in range(5):
            posts = await reddit_service.search_posts_by_keyword("test", limit=5)
            assert len(posts) == 1
            assert posts[0]["reddit_id"] == "reliable_post"
            assert posts[0]["title"] == "Reliable Post"
    
    @patch('httpx.AsyncClient')
    @pytest.mark.asyncio
    async def test_mock_oauth_service_reliability(self, mock_client_class):
        """Test OAuth mock service reliability."""
        # Mock client with consistent responses
        mock_client = MagicMock()
        mock_client_class.return_value.__aenter__.return_value = mock_client
        
        # Mock reliable token response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "access_token": "reliable_token",
            "token_type": "bearer",
            "expires_in": 3600,
            "refresh_token": "reliable_refresh",
            "scope": "identity"
        }
        mock_client.post.return_value = mock_response
        
        # Test repeated OAuth calls
        auth_service = AuthService()
        
        for i in range(3):
            token_data = await auth_service.exchange_code_for_token(f"code_{i}", f"state_{i}")
            assert token_data["access_token"] == "reliable_token"
            assert token_data["refresh_token"] == "reliable_refresh"