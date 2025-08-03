"""
Integration test for Reddit service.
Tests the service with realistic data structures.
"""

import pytest
import asyncio
from unittest.mock import Mock, patch
from datetime import datetime, timezone

from app.services.reddit_service import reddit_client, RedditPostData, RedditCommentData


class TestRedditServiceIntegration:
    """Integration tests for Reddit service."""
    
    @pytest.mark.asyncio
    async def test_reddit_client_initialization(self):
        """Test that Reddit client initializes properly."""
        assert reddit_client is not None
        assert reddit_client.reddit is not None
        assert reddit_client.rate_limiter is not None
    
    @pytest.mark.asyncio
    async def test_search_posts_integration(self):
        """Test searching posts with realistic mock data."""
        # Create realistic mock submission
        mock_submission = Mock()
        mock_submission.id = "abc123"
        mock_submission.title = "Interesting Python Discussion"
        mock_submission.selftext = "What are your thoughts on async programming?"
        mock_submission.author = Mock()
        mock_submission.author.__str__ = Mock(return_value="python_dev")
        mock_submission.score = 150
        mock_submission.num_comments = 45
        mock_submission.url = "https://reddit.com/r/Python/comments/abc123"
        mock_submission.subreddit = Mock()
        mock_submission.subreddit.__str__ = Mock(return_value="Python")
        mock_submission.created_utc = 1640995200  # 2022-01-01 00:00:00 UTC
        
        # Mock the Reddit API call
        with patch.object(reddit_client.reddit, 'subreddit') as mock_subreddit:
            mock_subreddit.return_value.search.return_value = [mock_submission]
            
            posts = await reddit_client.search_posts_by_keyword("python", limit=5)
            
            assert len(posts) == 1
            post = posts[0]
            assert isinstance(post, RedditPostData)
            assert post.reddit_id == "abc123"
            assert post.title == "Interesting Python Discussion"
            assert post.content == "What are your thoughts on async programming?"
            assert post.author == "python_dev"
            assert post.score == 150
            assert post.num_comments == 45
            assert post.subreddit == "Python"
            assert isinstance(post.created_at, datetime)
    
    @pytest.mark.asyncio
    async def test_get_comments_integration(self):
        """Test getting comments with realistic mock data."""
        # Create realistic mock comments
        mock_comment1 = Mock()
        mock_comment1.id = "comment1"
        mock_comment1.body = "Great question! I love async/await syntax."
        mock_comment1.author = Mock()
        mock_comment1.author.__str__ = Mock(return_value="async_fan")
        mock_comment1.score = 25
        mock_comment1.created_utc = 1640995800  # 10 minutes later
        
        mock_comment2 = Mock()
        mock_comment2.id = "comment2"
        mock_comment2.body = "I prefer traditional threading for some use cases."
        mock_comment2.author = Mock()
        mock_comment2.author.__str__ = Mock(return_value="thread_lover")
        mock_comment2.score = 15
        mock_comment2.created_utc = 1640996400  # 20 minutes later
        
        # Mock the submission and comments
        mock_submission = Mock()
        mock_comments = Mock()
        mock_comments.replace_more = Mock()
        mock_comments.__getitem__ = Mock(return_value=[mock_comment1, mock_comment2])
        mock_submission.comments = mock_comments
        
        with patch.object(reddit_client.reddit, 'submission') as mock_submission_method:
            mock_submission_method.return_value = mock_submission
            
            comments = await reddit_client.get_post_comments("abc123", limit=10)
            
            assert len(comments) == 2
            
            comment1 = comments[0]
            assert isinstance(comment1, RedditCommentData)
            assert comment1.reddit_id == "comment1"
            assert comment1.body == "Great question! I love async/await syntax."
            assert comment1.author == "async_fan"
            assert comment1.score == 25
            
            comment2 = comments[1]
            assert comment2.reddit_id == "comment2"
            assert comment2.body == "I prefer traditional threading for some use cases."
            assert comment2.author == "thread_lover"
            assert comment2.score == 15
    
    @pytest.mark.asyncio
    async def test_subreddit_posts_integration(self):
        """Test getting subreddit posts with realistic mock data."""
        # Create multiple realistic mock submissions
        mock_submissions = []
        for i in range(3):
            mock_submission = Mock()
            mock_submission.id = f"post{i}"
            mock_submission.title = f"Post Title {i}"
            mock_submission.selftext = f"Post content {i}"
            mock_submission.author = Mock()
            mock_submission.author.__str__ = Mock(return_value=f"user{i}")
            mock_submission.score = 100 + i * 10
            mock_submission.num_comments = 20 + i * 5
            mock_submission.url = f"https://reddit.com/r/test/comments/post{i}"
            mock_submission.subreddit = Mock()
            mock_submission.subreddit.__str__ = Mock(return_value="test")
            mock_submission.created_utc = 1640995200 + i * 3600  # 1 hour apart
            mock_submissions.append(mock_submission)
        
        # Mock the subreddit API call
        with patch.object(reddit_client.reddit, 'subreddit') as mock_subreddit:
            mock_subreddit.return_value.hot.return_value = mock_submissions
            
            posts = await reddit_client.get_subreddit_posts("test", limit=10, sort="hot")
            
            assert len(posts) == 3
            
            for i, post in enumerate(posts):
                assert isinstance(post, RedditPostData)
                assert post.reddit_id == f"post{i}"
                assert post.title == f"Post Title {i}"
                assert post.content == f"Post content {i}"
                assert post.author == f"user{i}"
                assert post.score == 100 + i * 10
                assert post.num_comments == 20 + i * 5
                assert post.subreddit == "test"
    
    @pytest.mark.asyncio
    async def test_health_check_integration(self):
        """Test health check functionality."""
        # Mock successful health check
        with patch.object(reddit_client.reddit, 'subreddit') as mock_subreddit:
            mock_test_subreddit = Mock()
            mock_test_subreddit.display_name = "test"
            mock_subreddit.return_value = mock_test_subreddit
            
            health = await reddit_client.health_check()
            
            assert health["status"] == "healthy"
            assert "Reddit API connection is working" in health["message"]
            assert "timestamp" in health
            
            # Verify the health check called the right endpoint
            mock_subreddit.assert_called_with("test")
    
    @pytest.mark.asyncio
    async def test_error_handling_integration(self):
        """Test error handling in Reddit service."""
        # Test API error handling
        with patch.object(reddit_client.reddit, 'subreddit') as mock_subreddit:
            mock_subreddit.return_value.search.side_effect = Exception("API Error")
            
            with pytest.raises(Exception):
                await reddit_client.search_posts_by_keyword("test", limit=5)
    
    @pytest.mark.asyncio
    async def test_rate_limiting_integration(self):
        """Test that rate limiting works properly."""
        # Test that rate limiter doesn't block normal usage
        start_time = asyncio.get_event_loop().time()
        await reddit_client.rate_limiter.wait_if_needed()
        await reddit_client.rate_limiter.wait_if_needed()
        end_time = asyncio.get_event_loop().time()
        
        # Should take at least 1 second due to per-second limit
        assert end_time - start_time >= 0.9


if __name__ == "__main__":
    pytest.main([__file__, "-v"])