"""
Test Reddit service implementation.
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime, timezone

from app.services.reddit_service import (
    RedditAPIClient, 
    RedditPostData, 
    RedditCommentData,
    RateLimiter
)


class TestRateLimiter:
    """Test rate limiter functionality."""
    
    @pytest.mark.asyncio
    async def test_rate_limiter_basic(self):
        """Test basic rate limiter functionality."""
        limiter = RateLimiter(requests_per_minute=60, requests_per_second=2)
        
        # First request should not wait
        start_time = asyncio.get_event_loop().time()
        await limiter.wait_if_needed()
        end_time = asyncio.get_event_loop().time()
        
        # Should be very fast (no waiting)
        assert end_time - start_time < 0.1
    
    @pytest.mark.asyncio
    async def test_rate_limiter_per_second(self):
        """Test per-second rate limiting."""
        limiter = RateLimiter(requests_per_minute=60, requests_per_second=1)
        
        # First request
        await limiter.wait_if_needed()
        
        # Second request should wait
        start_time = asyncio.get_event_loop().time()
        await limiter.wait_if_needed()
        end_time = asyncio.get_event_loop().time()
        
        # Should wait approximately 1 second
        assert end_time - start_time >= 0.9


class TestRedditAPIClient:
    """Test Reddit API client functionality."""
    
    @pytest.fixture
    def mock_reddit_client(self):
        """Create a mock Reddit client."""
        with patch('app.services.reddit_service.praw.Reddit') as mock_reddit:
            client = RedditAPIClient()
            client.reddit = mock_reddit.return_value
            return client
    
    @pytest.fixture
    def mock_submission(self):
        """Create a mock Reddit submission."""
        submission = Mock()
        submission.id = "test123"
        submission.title = "Test Post Title"
        submission.selftext = "Test post content"
        submission.author = Mock()
        submission.author.__str__ = Mock(return_value="test_user")
        submission.score = 100
        submission.num_comments = 25
        submission.url = "https://reddit.com/r/test/comments/test123"
        submission.subreddit = Mock()
        submission.subreddit.__str__ = Mock(return_value="test")
        submission.created_utc = 1640995200  # 2022-01-01 00:00:00 UTC
        return submission
    
    @pytest.fixture
    def mock_comment(self):
        """Create a mock Reddit comment."""
        comment = Mock()
        comment.id = "comment123"
        comment.body = "Test comment body"
        comment.author = Mock()
        comment.author.__str__ = Mock(return_value="comment_user")
        comment.score = 10
        comment.created_utc = 1640995200  # 2022-01-01 00:00:00 UTC
        return comment
    
    def test_normalize_post_data(self, mock_reddit_client, mock_submission):
        """Test post data normalization."""
        post_data = mock_reddit_client._normalize_post_data(mock_submission)
        
        assert isinstance(post_data, RedditPostData)
        assert post_data.reddit_id == "test123"
        assert post_data.title == "Test Post Title"
        assert post_data.content == "Test post content"
        assert post_data.author == "test_user"
        assert post_data.score == 100
        assert post_data.num_comments == 25
        assert post_data.subreddit == "test"
        assert isinstance(post_data.created_at, datetime)
    
    def test_normalize_comment_data(self, mock_reddit_client, mock_comment):
        """Test comment data normalization."""
        comment_data = mock_reddit_client._normalize_comment_data(mock_comment)
        
        assert isinstance(comment_data, RedditCommentData)
        assert comment_data.reddit_id == "comment123"
        assert comment_data.body == "Test comment body"
        assert comment_data.author == "comment_user"
        assert comment_data.score == 10
        assert isinstance(comment_data.created_at, datetime)
    
    @pytest.mark.asyncio
    async def test_search_posts_by_keyword(self, mock_reddit_client, mock_submission):
        """Test searching posts by keyword."""
        # Mock the search results
        mock_reddit_client.reddit.subreddit.return_value.search.return_value = [mock_submission]
        
        posts = await mock_reddit_client.search_posts_by_keyword("test", limit=10)
        
        assert len(posts) == 1
        assert isinstance(posts[0], RedditPostData)
        assert posts[0].reddit_id == "test123"
        
        # Verify the search was called correctly
        mock_reddit_client.reddit.subreddit.assert_called_with("all")
        mock_reddit_client.reddit.subreddit.return_value.search.assert_called_with(
            "test", sort="hot", time_filter="week", limit=10
        )
    
    @pytest.mark.asyncio
    async def test_get_post_comments(self, mock_reddit_client, mock_comment):
        """Test getting post comments."""
        # Mock the submission and comments
        mock_submission = Mock()
        mock_comments = Mock()
        mock_comments.replace_more = Mock()
        mock_comments.__iter__ = Mock(return_value=iter([mock_comment]))
        mock_comments.__getitem__ = Mock(return_value=[mock_comment])
        mock_submission.comments = mock_comments
        mock_reddit_client.reddit.submission.return_value = mock_submission
        
        comments = await mock_reddit_client.get_post_comments("test123", limit=10)
        
        assert len(comments) == 1
        assert isinstance(comments[0], RedditCommentData)
        assert comments[0].reddit_id == "comment123"
        
        # Verify the submission was fetched correctly
        mock_reddit_client.reddit.submission.assert_called_with(id="test123")
    
    @pytest.mark.asyncio
    async def test_get_subreddit_posts(self, mock_reddit_client, mock_submission):
        """Test getting posts from a subreddit."""
        # Mock the subreddit posts
        mock_subreddit = Mock()
        mock_subreddit.hot.return_value = [mock_submission]
        mock_reddit_client.reddit.subreddit.return_value = mock_subreddit
        
        posts = await mock_reddit_client.get_subreddit_posts("test", limit=10, sort="hot")
        
        assert len(posts) == 1
        assert isinstance(posts[0], RedditPostData)
        assert posts[0].reddit_id == "test123"
        
        # Verify the subreddit was accessed correctly
        mock_reddit_client.reddit.subreddit.assert_called_with("test")
        mock_subreddit.hot.assert_called_with(limit=10)
    
    @pytest.mark.asyncio
    async def test_health_check_healthy(self, mock_reddit_client):
        """Test health check when Reddit API is healthy."""
        # Mock successful API access
        mock_subreddit = Mock()
        mock_subreddit.display_name = "test"
        mock_reddit_client.reddit.subreddit.return_value = mock_subreddit
        
        health = await mock_reddit_client.health_check()
        
        assert health["status"] == "healthy"
        assert "Reddit API connection is working" in health["message"]
        assert "timestamp" in health
    
    @pytest.mark.asyncio
    async def test_health_check_unhealthy(self, mock_reddit_client):
        """Test health check when Reddit API is unhealthy."""
        # Mock API failure
        mock_reddit_client.reddit.subreddit.side_effect = Exception("API Error")
        
        health = await mock_reddit_client.health_check()
        
        assert health["status"] == "unhealthy"
        assert "Reddit API connection failed" in health["message"]
        assert "timestamp" in health


if __name__ == "__main__":
    pytest.main([__file__, "-v"])