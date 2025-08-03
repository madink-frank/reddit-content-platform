"""
Simple test for Reddit service functionality.
"""

import pytest
import asyncio
from unittest.mock import Mock, patch
from datetime import datetime, timezone

from app.services.reddit_service import (
    reddit_client, 
    RedditAPIClient, 
    RedditPostData, 
    RedditCommentData,
    RateLimiter
)


class TestRedditServiceSimple:
    """Simple tests for Reddit service core functionality."""
    
    def test_reddit_client_exists(self):
        """Test that Reddit client is properly initialized."""
        assert reddit_client is not None
        assert isinstance(reddit_client, RedditAPIClient)
        assert reddit_client.reddit is not None
        assert reddit_client.rate_limiter is not None
    
    def test_reddit_post_data_structure(self):
        """Test RedditPostData structure."""
        post_data = RedditPostData(
            reddit_id="test123",
            title="Test Title",
            content="Test content",
            author="test_author",
            score=100,
            num_comments=25,
            url="https://reddit.com/test",
            subreddit="test",
            created_at=datetime.now(timezone.utc)
        )
        
        assert post_data.reddit_id == "test123"
        assert post_data.title == "Test Title"
        assert post_data.content == "Test content"
        assert post_data.author == "test_author"
        assert post_data.score == 100
        assert post_data.num_comments == 25
        assert post_data.url == "https://reddit.com/test"
        assert post_data.subreddit == "test"
        assert isinstance(post_data.created_at, datetime)
    
    def test_reddit_comment_data_structure(self):
        """Test RedditCommentData structure."""
        comment_data = RedditCommentData(
            reddit_id="comment123",
            body="Test comment body",
            author="comment_author",
            score=10,
            created_at=datetime.now(timezone.utc)
        )
        
        assert comment_data.reddit_id == "comment123"
        assert comment_data.body == "Test comment body"
        assert comment_data.author == "comment_author"
        assert comment_data.score == 10
        assert isinstance(comment_data.created_at, datetime)
    
    def test_rate_limiter_initialization(self):
        """Test rate limiter initialization."""
        limiter = RateLimiter(requests_per_minute=60, requests_per_second=1)
        
        assert limiter.requests_per_minute == 60
        assert limiter.requests_per_second == 1
        assert limiter.minute_requests == []
        assert limiter.last_request_time == 0
    
    @pytest.mark.asyncio
    async def test_rate_limiter_functionality(self):
        """Test basic rate limiter functionality."""
        limiter = RateLimiter(requests_per_minute=120, requests_per_second=2)
        
        # First call should be fast
        start_time = asyncio.get_event_loop().time()
        await limiter.wait_if_needed()
        end_time = asyncio.get_event_loop().time()
        
        # Should be very fast (no waiting)
        assert end_time - start_time < 0.1
        
        # Check that request was recorded
        assert len(limiter.minute_requests) == 1
    
    def test_normalize_post_data_with_mock(self):
        """Test post data normalization with mock submission."""
        client = RedditAPIClient()
        
        # Create mock submission
        mock_submission = Mock()
        mock_submission.id = "test123"
        mock_submission.title = "Test Post Title"
        mock_submission.selftext = "Test post content"
        mock_submission.author = Mock()
        mock_submission.author.__str__ = Mock(return_value="test_user")
        mock_submission.score = 100
        mock_submission.num_comments = 25
        mock_submission.url = "https://reddit.com/r/test/comments/test123"
        mock_submission.subreddit = Mock()
        mock_submission.subreddit.__str__ = Mock(return_value="test")
        mock_submission.created_utc = 1640995200  # 2022-01-01 00:00:00 UTC
        
        # Test normalization
        post_data = client._normalize_post_data(mock_submission)
        
        assert isinstance(post_data, RedditPostData)
        assert post_data.reddit_id == "test123"
        assert post_data.title == "Test Post Title"
        assert post_data.content == "Test post content"
        assert post_data.author == "test_user"
        assert post_data.score == 100
        assert post_data.num_comments == 25
        assert post_data.subreddit == "test"
        assert isinstance(post_data.created_at, datetime)
    
    def test_normalize_comment_data_with_mock(self):
        """Test comment data normalization with mock comment."""
        client = RedditAPIClient()
        
        # Create mock comment
        mock_comment = Mock()
        mock_comment.id = "comment123"
        mock_comment.body = "Test comment body"
        mock_comment.author = Mock()
        mock_comment.author.__str__ = Mock(return_value="comment_user")
        mock_comment.score = 10
        mock_comment.created_utc = 1640995200  # 2022-01-01 00:00:00 UTC
        
        # Test normalization
        comment_data = client._normalize_comment_data(mock_comment)
        
        assert isinstance(comment_data, RedditCommentData)
        assert comment_data.reddit_id == "comment123"
        assert comment_data.body == "Test comment body"
        assert comment_data.author == "comment_user"
        assert comment_data.score == 10
        assert isinstance(comment_data.created_at, datetime)
    
    @pytest.mark.asyncio
    async def test_search_posts_with_mock(self):
        """Test searching posts with mocked Reddit API."""
        client = RedditAPIClient()
        
        # Create mock submission
        mock_submission = Mock()
        mock_submission.id = "search123"
        mock_submission.title = "Search Result Post"
        mock_submission.selftext = "Search result content"
        mock_submission.author = Mock()
        mock_submission.author.__str__ = Mock(return_value="search_user")
        mock_submission.score = 150
        mock_submission.num_comments = 30
        mock_submission.url = "https://reddit.com/r/python/comments/search123"
        mock_submission.subreddit = Mock()
        mock_submission.subreddit.__str__ = Mock(return_value="python")
        mock_submission.created_utc = 1640995200
        
        # Mock the Reddit API call
        with patch.object(client.reddit, 'subreddit') as mock_subreddit:
            mock_subreddit.return_value.search.return_value = [mock_submission]
            
            posts = await client.search_posts_by_keyword("python", limit=5)
            
            assert len(posts) == 1
            post = posts[0]
            assert isinstance(post, RedditPostData)
            assert post.reddit_id == "search123"
            assert post.title == "Search Result Post"
            assert post.content == "Search result content"
            assert post.author == "search_user"
            assert post.score == 150
            assert post.subreddit == "python"
    
    @pytest.mark.asyncio
    async def test_health_check_success(self):
        """Test successful health check."""
        client = RedditAPIClient()
        
        # Mock successful API access
        with patch.object(client.reddit, 'subreddit') as mock_subreddit:
            mock_test_subreddit = Mock()
            mock_test_subreddit.display_name = "test"
            mock_subreddit.return_value = mock_test_subreddit
            
            health = await client.health_check()
            
            assert health["status"] == "healthy"
            assert "Reddit API connection is working" in health["message"]
            assert "timestamp" in health
    
    @pytest.mark.asyncio
    async def test_health_check_failure(self):
        """Test failed health check."""
        client = RedditAPIClient()
        
        # Mock API failure
        with patch.object(client.reddit, 'subreddit') as mock_subreddit:
            mock_subreddit.side_effect = Exception("Connection failed")
            
            health = await client.health_check()
            
            assert health["status"] == "unhealthy"
            assert "Reddit API connection failed" in health["message"]
            assert "timestamp" in health


if __name__ == "__main__":
    pytest.main([__file__, "-v"])