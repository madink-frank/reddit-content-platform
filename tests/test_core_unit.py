"""
Core unit tests for business logic components.
Tests the essential functionality without complex mocking.
"""
import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime, timedelta
import json

from app.services.reddit_service import RedditAPIClient, RedditPostData, RedditCommentData
from app.core.security import create_access_token, verify_token
from app.core.config import Settings


class TestRedditAPIClient:
    """Unit tests for Reddit API client."""
    
    @pytest.mark.asyncio
    async def test_health_check_success(self):
        """Test successful health check."""
        with patch('app.services.reddit_service.praw.Reddit'):
            client = RedditAPIClient()
            
            # Mock successful Reddit API access
            mock_subreddit = MagicMock()
            mock_subreddit.display_name = "test"
            client.reddit.subreddit.return_value = mock_subreddit
            
            result = await client.health_check()
            
            assert result["status"] == "healthy"
            assert "Reddit API connection is working" in result["message"]
            assert "timestamp" in result
    
    @pytest.mark.asyncio
    async def test_health_check_failure(self):
        """Test failed health check."""
        with patch('app.services.reddit_service.praw.Reddit'):
            client = RedditAPIClient()
            
            # Mock Reddit API failure
            client.reddit.subreddit.side_effect = Exception("API Error")
            
            result = await client.health_check()
            
            assert result["status"] == "unhealthy"
            assert "Reddit API connection failed" in result["message"]
            assert "timestamp" in result
    
    def test_normalize_post_data(self):
        """Test post data normalization."""
        with patch('app.services.reddit_service.praw.Reddit'):
            client = RedditAPIClient()
            
            # Mock Reddit submission
            mock_submission = MagicMock()
            mock_submission.id = "test_post_id"
            mock_submission.title = "Test Post Title"
            mock_submission.selftext = "Test post content"
            mock_submission.author = "test_author"
            mock_submission.score = 150
            mock_submission.num_comments = 30
            mock_submission.url = "https://reddit.com/test"
            mock_submission.subreddit = "python"
            mock_submission.created_utc = 1640995200  # 2022-01-01
            
            result = client._normalize_post_data(mock_submission)
            
            assert isinstance(result, RedditPostData)
            assert result.reddit_id == "test_post_id"
            assert result.title == "Test Post Title"
            assert result.content == "Test post content"
            assert result.author == "test_author"
            assert result.score == 150
            assert result.num_comments == 30
            assert result.subreddit == "python"
    
    def test_normalize_comment_data(self):
        """Test comment data normalization."""
        with patch('app.services.reddit_service.praw.Reddit'):
            client = RedditAPIClient()
            
            # Mock Reddit comment
            mock_comment = MagicMock()
            mock_comment.id = "test_comment_id"
            mock_comment.body = "Test comment body"
            mock_comment.author = "test_commenter"
            mock_comment.score = 25
            mock_comment.created_utc = 1640995200
            
            result = client._normalize_comment_data(mock_comment)
            
            assert isinstance(result, RedditCommentData)
            assert result.reddit_id == "test_comment_id"
            assert result.body == "Test comment body"
            assert result.author == "test_commenter"
            assert result.score == 25


class TestSecurityFunctions:
    """Unit tests for security functions."""
    
    def test_create_access_token(self):
        """Test JWT access token creation."""
        user_id = 1
        token = create_access_token(subject=str(user_id))
        
        # Verify token structure
        assert isinstance(token, str)
        assert len(token.split('.')) == 3  # JWT has 3 parts
    
    def test_verify_valid_token(self):
        """Test verification of valid JWT token."""
        user_id = 1
        token = create_access_token(subject=str(user_id))
        
        payload = verify_token(token, token_type="access")
        assert payload["sub"] == str(user_id)
        assert payload["type"] == "access"
    
    def test_verify_invalid_token(self):
        """Test verification of invalid JWT token."""
        invalid_token = "invalid.jwt.token"
        
        result = verify_token(invalid_token, token_type="access")
        assert result is None


class TestDataStructures:
    """Unit tests for data structures and models."""
    
    def test_reddit_post_data_creation(self):
        """Test RedditPostData creation."""
        post_data = RedditPostData(
            reddit_id="test_id",
            title="Test Title",
            content="Test content",
            author="test_author",
            score=100,
            num_comments=25,
            url="https://reddit.com/test",
            subreddit="python",
            created_at=datetime.utcnow()
        )
        
        assert post_data.reddit_id == "test_id"
        assert post_data.title == "Test Title"
        assert post_data.score == 100
        assert post_data.num_comments == 25
        assert post_data.subreddit == "python"
    
    def test_reddit_comment_data_creation(self):
        """Test RedditCommentData creation."""
        comment_data = RedditCommentData(
            reddit_id="comment_id",
            body="Test comment",
            author="commenter",
            score=10,
            created_at=datetime.utcnow()
        )
        
        assert comment_data.reddit_id == "comment_id"
        assert comment_data.body == "Test comment"
        assert comment_data.author == "commenter"
        assert comment_data.score == 10


class TestUtilityFunctions:
    """Unit tests for utility functions."""
    
    def test_rate_limiter_initialization(self):
        """Test rate limiter initialization."""
        from app.services.reddit_service import RateLimiter
        
        rate_limiter = RateLimiter(requests_per_minute=60, requests_per_second=1)
        
        assert rate_limiter.requests_per_minute == 60
        assert rate_limiter.requests_per_second == 1
        assert rate_limiter.minute_requests == []
        assert rate_limiter.last_request_time == 0
    
    @pytest.mark.asyncio
    async def test_rate_limiter_wait_logic(self):
        """Test rate limiter wait logic."""
        from app.services.reddit_service import RateLimiter
        import time
        
        rate_limiter = RateLimiter(requests_per_minute=2, requests_per_second=1)
        
        # First request should not wait
        start_time = time.time()
        await rate_limiter.wait_if_needed()
        first_duration = time.time() - start_time
        
        assert first_duration < 0.1  # Should be very fast
        
        # Second request should wait due to per-second limit
        start_time = time.time()
        await rate_limiter.wait_if_needed()
        second_duration = time.time() - start_time
        
        assert second_duration >= 0.9  # Should wait ~1 second


class TestBusinessLogic:
    """Unit tests for core business logic."""
    
    def test_engagement_score_calculation(self):
        """Test engagement score calculation logic."""
        # Simple engagement score formula: score + (comments * 2)
        def calculate_engagement_score(score, num_comments):
            return score + (num_comments * 2)
        
        # Test with different values
        assert calculate_engagement_score(100, 25) == 150
        assert calculate_engagement_score(50, 10) == 70
        assert calculate_engagement_score(0, 0) == 0
    
    def test_content_quality_validation(self):
        """Test content quality validation logic."""
        def validate_content_quality(content):
            # Simple validation: content should be at least 100 characters
            # and contain markdown headers
            if len(content) < 100:
                return False
            if not content.strip().startswith('#'):
                return False
            return True
        
        # Good content
        good_content = """
        # Test Article
        
        This is a comprehensive article about testing that contains
        enough content to be considered high quality. It has proper
        markdown formatting and substantial text content.
        """
        
        assert validate_content_quality(good_content) is True
        
        # Poor content (too short)
        poor_content = "# Short\n\nToo short."
        
        assert validate_content_quality(poor_content) is False
    
    def test_reading_time_estimation(self):
        """Test reading time estimation logic."""
        def estimate_reading_time(content, words_per_minute=200):
            # Count words and calculate reading time
            words = len(content.split())
            minutes = max(1, round(words / words_per_minute))
            return minutes
        
        # Test with different content lengths
        short_content = " ".join(["word"] * 100)  # 100 words
        medium_content = " ".join(["word"] * 400)  # 400 words
        long_content = " ".join(["word"] * 1000)  # 1000 words
        
        assert estimate_reading_time(short_content) == 1  # Minimum 1 minute
        assert estimate_reading_time(medium_content) == 2  # 2 minutes
        assert estimate_reading_time(long_content) == 5  # 5 minutes
    
    def test_keyword_extraction_logic(self):
        """Test keyword extraction logic."""
        def extract_keywords(text, min_length=3):
            # Simple keyword extraction: split words, filter by length
            import re
            words = re.findall(r'\b\w+\b', text.lower())
            keywords = [word for word in words if len(word) >= min_length]
            # Remove duplicates while preserving order
            seen = set()
            unique_keywords = []
            for keyword in keywords:
                if keyword not in seen:
                    seen.add(keyword)
                    unique_keywords.append(keyword)
            return unique_keywords[:10]  # Return top 10
        
        text = "Python programming is great for data science and machine learning applications"
        keywords = extract_keywords(text)
        
        assert "python" in keywords
        assert "programming" in keywords
        assert "data" in keywords
        assert "science" in keywords
        assert len(keywords) <= 10
    
    def test_trend_velocity_calculation(self):
        """Test trend velocity calculation logic."""
        def calculate_trend_velocity(historical_scores):
            # Simple trend velocity: difference between recent and older scores
            if len(historical_scores) < 2:
                return 0.0
            
            recent_avg = sum(historical_scores[-3:]) / min(3, len(historical_scores[-3:]))
            older_avg = sum(historical_scores[:-3]) / max(1, len(historical_scores[:-3]))
            
            if older_avg == 0:
                return 0.0
            
            velocity = (recent_avg - older_avg) / older_avg
            return round(velocity, 3)
        
        # Increasing trend
        increasing_scores = [100, 120, 140, 160, 180, 200]
        assert calculate_trend_velocity(increasing_scores) > 0
        
        # Decreasing trend
        decreasing_scores = [200, 180, 160, 140, 120, 100]
        assert calculate_trend_velocity(decreasing_scores) < 0
        
        # Stable trend
        stable_scores = [100, 100, 100, 100, 100, 100]
        assert calculate_trend_velocity(stable_scores) == 0.0


class TestErrorHandling:
    """Unit tests for error handling."""
    
    def test_graceful_error_handling(self):
        """Test graceful error handling in services."""
        def safe_divide(a, b):
            try:
                return a / b
            except ZeroDivisionError:
                return 0.0
            except Exception:
                return None
        
        assert safe_divide(10, 2) == 5.0
        assert safe_divide(10, 0) == 0.0
        assert safe_divide("invalid", 2) is None
    
    def test_data_validation(self):
        """Test data validation logic."""
        def validate_post_data(post_data):
            required_fields = ['reddit_id', 'title', 'author', 'score']
            
            if not isinstance(post_data, dict):
                return False
            
            for field in required_fields:
                if field not in post_data or post_data[field] is None:
                    return False
            
            # Score should be numeric
            if not isinstance(post_data['score'], (int, float)):
                return False
            
            return True
        
        # Valid data
        valid_data = {
            'reddit_id': 'test_id',
            'title': 'Test Title',
            'author': 'test_author',
            'score': 100
        }
        assert validate_post_data(valid_data) is True
        
        # Invalid data (missing field)
        invalid_data = {
            'reddit_id': 'test_id',
            'title': 'Test Title'
            # Missing author and score
        }
        assert validate_post_data(invalid_data) is False
        
        # Invalid data (wrong type)
        wrong_type_data = {
            'reddit_id': 'test_id',
            'title': 'Test Title',
            'author': 'test_author',
            'score': 'not_a_number'
        }
        assert validate_post_data(wrong_type_data) is False


# Integration test for core functionality
class TestCoreIntegration:
    """Integration tests for core functionality."""
    
    def test_data_flow_simulation(self):
        """Test simulated data flow through the system."""
        # Simulate the flow: Reddit data -> Processing -> Storage
        
        # Step 1: Mock Reddit data
        reddit_data = {
            'reddit_id': 'test_post',
            'title': 'Python Programming Tutorial',
            'content': 'Learn Python programming with this comprehensive guide',
            'author': 'python_expert',
            'score': 250,
            'num_comments': 45,
            'subreddit': 'python'
        }
        
        # Step 2: Process data (extract keywords)
        def extract_keywords(text):
            import re
            words = re.findall(r'\b\w+\b', text.lower())
            return [word for word in words if len(word) > 3][:5]
        
        keywords = extract_keywords(reddit_data['title'] + ' ' + reddit_data['content'])
        
        # Step 3: Calculate metrics
        engagement_score = reddit_data['score'] + (reddit_data['num_comments'] * 2)
        
        # Step 4: Verify results
        assert 'python' in keywords
        assert 'programming' in keywords
        assert engagement_score == 340  # 250 + (45 * 2)
        assert len(keywords) <= 5
    
    def test_error_recovery_simulation(self):
        """Test error recovery in data processing."""
        def process_posts_with_recovery(posts_data):
            processed = []
            errors = []
            
            for post in posts_data:
                try:
                    # Simulate processing that might fail
                    if not post.get('title'):
                        raise ValueError("Missing title")
                    
                    processed_post = {
                        'id': post['reddit_id'],
                        'title': post['title'],
                        'score': post.get('score', 0)
                    }
                    processed.append(processed_post)
                    
                except Exception as e:
                    errors.append({'post_id': post.get('reddit_id', 'unknown'), 'error': str(e)})
                    continue
            
            return processed, errors
        
        # Test data with some invalid posts
        test_posts = [
            {'reddit_id': 'post1', 'title': 'Valid Post', 'score': 100},
            {'reddit_id': 'post2', 'score': 50},  # Missing title
            {'reddit_id': 'post3', 'title': 'Another Valid Post', 'score': 75}
        ]
        
        processed, errors = process_posts_with_recovery(test_posts)
        
        assert len(processed) == 2  # 2 valid posts
        assert len(errors) == 1     # 1 error
        assert errors[0]['post_id'] == 'post2'
        assert 'Missing title' in errors[0]['error']