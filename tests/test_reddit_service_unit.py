"""
Unit tests for Reddit API Client (Crawling Logic).
"""
import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from datetime import datetime, timezone
import praw
from prawcore.exceptions import ResponseException, RequestException

from app.services.reddit_service import RedditAPIClient, RedditPostData, RedditCommentData, RateLimiter


class TestRateLimiter:
    """Test cases for RateLimiter."""
    
    @pytest.fixture
    def rate_limiter(self):
        """Create RateLimiter instance for testing."""
        return RateLimiter(calls_per_minute=60)
    
    def test_rate_limiter_initialization(self, rate_limiter):
        """Test rate limiter initialization."""
        assert rate_limiter.calls_per_minute == 60
        assert rate_limiter.call_times == []
    
    def test_can_make_call_empty_history(self, rate_limiter):
        """Test can_make_call with empty call history."""
        assert rate_limiter.can_make_call() is True
    
    def test_record_call(self, rate_limiter):
        """Test recording a call."""
        initial_count = len(rate_limiter.call_times)
        rate_limiter.record_call()
        assert len(rate_limiter.call_times) == initial_count + 1


class TestRedditAPIClient:
    """Test cases for RedditAPIClient."""
    
    @pytest.fixture
    def reddit_client(self):
        """Create RedditAPIClient instance for testing."""
        return RedditAPIClient()
    
    @pytest.fixture
    def mock_reddit_instance(self):
        """Mock Reddit API instance."""
        reddit_mock = MagicMock()
        
        # Mock submission
        submission_mock = MagicMock()
        submission_mock.id = "test_post_id"
        submission_mock.title = "Test Post Title"
        submission_mock.selftext = "This is test post content"
        submission_mock.author.name = "test_author"
        submission_mock.score = 100
        submission_mock.num_comments = 25
        submission_mock.url = "https://reddit.com/r/test/comments/test_post_id"
        submission_mock.created_utc = 1640995200.0  # 2022-01-01
        submission_mock.subreddit.display_name = "test"
        
        # Mock comment
        comment_mock = MagicMock()
        comment_mock.id = "test_comment_id"
        comment_mock.body = "Test comment body"
        comment_mock.author.name = "test_commenter"
        comment_mock.score = 10
        comment_mock.created_utc = 1640995200.0
        
        submission_mock.comments.list.return_value = [comment_mock]
        
        # Mock subreddit search
        reddit_mock.subreddit.return_value.search.return_value = [submission_mock]
        reddit_mock.submission.return_value = submission_mock
        
        return reddit_mock
    
    def test_reddit_client_initialization(self, reddit_client):
        """Test Reddit client initialization."""
        assert reddit_client.rate_limiter is not None
        assert reddit_client.reddit_client is None  # Not initialized until first use
    
    @patch('app.services.reddit_service.praw.Reddit')
    def test_initialize_reddit_client_success(self, mock_reddit, reddit_client):
        """Test successful Reddit client initialization."""
        mock_reddit.return_value = MagicMock()
        
        client = reddit_client._initialize_reddit_client()
        
        assert client is not None
        mock_reddit.assert_called_once()
    
    def test_normalize_post_data(self, reddit_client):
        """Test post data normalization."""
        # Mock submission object
        submission_mock = MagicMock()
        submission_mock.id = "test_post_id"
        submission_mock.title = "Test Post Title"
        submission_mock.selftext = "This is test post content"
        submission_mock.author.name = "test_author"
        submission_mock.score = 100
        submission_mock.num_comments = 25
        submission_mock.url = "https://reddit.com/r/test/comments/test_post_id"
        submission_mock.created_utc = 1640995200.0
        submission_mock.subreddit.display_name = "test"
        
        post_data = reddit_client._normalize_post_data(submission_mock)
        
        assert isinstance(post_data, RedditPostData)
        assert post_data.reddit_id == "test_post_id"
        assert post_data.title == "Test Post Title"
        assert post_data.content == "This is test post content"
        assert post_data.author == "test_author"
        assert post_data.score == 100
        assert post_data.num_comments == 25
        assert post_data.subreddit == "test"
    
    def test_normalize_comment_data(self, reddit_client):
        """Test comment data normalization."""
        # Mock comment object
        comment_mock = MagicMock()
        comment_mock.id = "test_comment_id"
        comment_mock.body = "Test comment body"
        comment_mock.author.name = "test_commenter"
        comment_mock.score = 10
        
        comment_data = reddit_client._normalize_comment_data(comment_mock)
        
        assert isinstance(comment_data, RedditCommentData)
        assert comment_data.reddit_id == "test_comment_id"
        assert comment_data.body == "Test comment body"
        assert comment_data.author == "test_commenter"
        assert comment_data.score == 10
    
    def test_handle_deleted_author(self, reddit_client):
        """Test handling of deleted author."""
        # Mock submission with deleted author
        submission_mock = MagicMock()
        submission_mock.id = "test_post_id"
        submission_mock.title = "Test Post Title"
        submission_mock.selftext = "This is test post content"
        submission_mock.author = None  # Deleted author
        submission_mock.score = 100
        submission_mock.num_comments = 25
        submission_mock.url = "https://reddit.com/r/test/comments/test_post_id"
        submission_mock.created_utc = 1640995200.0
        submission_mock.subreddit.display_name = "test"
        
        post_data = reddit_client._normalize_post_data(submission_mock)
        
        assert post_data.author == "[deleted]"
    
    def test_handle_empty_content(self, reddit_client):
        """Test handling of empty post content."""
        # Mock submission with no selftext
        submission_mock = MagicMock()
        submission_mock.id = "test_post_id"
        submission_mock.title = "Test Post Title"
        submission_mock.selftext = ""
        submission_mock.author.name = "test_author"
        submission_mock.score = 100
        submission_mock.num_comments = 25
        submission_mock.url = "https://reddit.com/r/test/comments/test_post_id"
        submission_mock.created_utc = 1640995200.0
        submission_mock.subreddit.display_name = "test"
        
        post_data = reddit_client._normalize_post_data(submission_mock)
        
        assert post_data.content == ""
    
    @patch('app.services.reddit_service.praw.Reddit')
    def test_search_posts_success(self, mock_reddit, reddit_client, mock_reddit_instance):
        """Test successful post search."""
        mock_reddit.return_value = mock_reddit_instance
        
        posts = reddit_client.search_posts("python", limit=10)
        
        assert len(posts) == 1
        assert isinstance(posts[0], RedditPostData)
        assert posts[0].reddit_id == "test_post_id"
    
    @patch('app.services.reddit_service.praw.Reddit')
    def test_search_posts_with_rate_limiting(self, mock_reddit, reddit_client):
        """Test post search with rate limiting."""
        mock_reddit_instance = MagicMock()
        mock_reddit.return_value = mock_reddit_instance
        
        # Mock rate limiter to deny first call
        reddit_client.rate_limiter.can_make_call = MagicMock(side_effect=[False, True])
        
        with patch('time.sleep') as mock_sleep:
            posts = reddit_client.search_posts("python", limit=10)
            mock_sleep.assert_called_once()
    
    def test_validate_search_parameters_valid(self, reddit_client):
        """Test validation of valid search parameters."""
        # Should not raise any exception
        reddit_client._validate_search_parameters("python", 10, "all")
    
    def test_validate_search_parameters_empty_keyword(self, reddit_client):
        """Test validation with empty keyword."""
        with pytest.raises(ValueError, match="Keyword cannot be empty"):
            reddit_client._validate_search_parameters("", 10, "all")
    
    def test_validate_search_parameters_invalid_limit(self, reddit_client):
        """Test validation with invalid limit."""
        with pytest.raises(ValueError, match="Limit must be between 1 and 100"):
            reddit_client._validate_search_parameters("python", 0, "all")
        
        with pytest.raises(ValueError, match="Limit must be between 1 and 100"):
            reddit_client._validate_search_parameters("python", 101, "all")
    
    @patch('app.services.reddit_service.praw.Reddit')
    def test_get_comments_success(self, mock_reddit, reddit_client, mock_reddit_instance):
        """Test successful comment retrieval."""
        mock_reddit.return_value = mock_reddit_instance
        
        comments = reddit_client.get_comments("test_post_id", limit=10)
        
        assert len(comments) == 1
        assert isinstance(comments[0], RedditCommentData)
        assert comments[0].reddit_id == "test_comment_id"
    
    @patch('app.services.reddit_service.praw.Reddit')
    def test_handle_api_exception(self, mock_reddit, reddit_client):
        """Test handling of Reddit API exceptions."""
        mock_reddit_instance = MagicMock()
        mock_reddit_instance.subreddit.return_value.search.side_effect = ResponseException(MagicMock())
        mock_reddit.return_value = mock_reddit_instance
        
        with pytest.raises(Exception):
            reddit_client.search_posts("python", limit=10)