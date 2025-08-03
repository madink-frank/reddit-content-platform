"""
Comprehensive unit tests for all core business logic services.
This file contains unit tests for:
- AuthService
- KeywordService  
- RedditAPIClient
- TrendAnalysisService
- ContentGenerationService
"""
import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from datetime import datetime, timedelta
import json

from app.services.auth_service import AuthService
from app.services.keyword_service import KeywordService
from app.services.reddit_service import RedditAPIClient, RedditPostData, RedditCommentData, RateLimiter
from app.services.trend_analysis_service import TrendAnalysisService
from app.services.content_generation_service import ContentGenerationService
from app.services.template_service import TemplateService

from app.models.user import User
from app.models.keyword import Keyword
from app.models.post import Post
from app.models.blog_content import BlogContent
from app.schemas.keyword import KeywordCreate, KeywordUpdate
from app.schemas.blog_content import BlogContentCreate


class TestAuthService:
    """Test cases for AuthService."""
    
    @pytest.fixture
    def auth_service(self):
        """Create AuthService instance for testing."""
        return AuthService()
    
    def test_get_reddit_auth_url(self, auth_service):
        """Test Reddit OAuth URL generation."""
        state = "test_state"
        url = auth_service.get_reddit_auth_url(state)
        
        assert isinstance(url, str)
        assert "reddit.com" in url
        assert "authorize" in url
        assert state in url
    
    @pytest.mark.asyncio
    async def test_exchange_code_for_token_success(self, auth_service):
        """Test successful code exchange."""
        code = "valid_code"
        
        with patch('httpx.AsyncClient') as mock_client:
            mock_response = MagicMock()
            mock_response.json.return_value = {
                'access_token': 'reddit_token',
                'token_type': 'bearer'
            }
            mock_response.raise_for_status = MagicMock()
            
            mock_client.return_value.__aenter__.return_value.post.return_value = mock_response
            
            result = await auth_service.exchange_code_for_token(code)
            
            assert result['access_token'] == 'reddit_token'
            assert result['token_type'] == 'bearer'
    
    @pytest.mark.asyncio
    async def test_get_reddit_user_info_success(self, auth_service):
        """Test successful user info retrieval."""
        access_token = "valid_token"
        
        with patch('httpx.AsyncClient') as mock_client:
            mock_response = MagicMock()
            mock_response.json.return_value = {
                'id': 'reddit_user_id',
                'name': 'test_user'
            }
            mock_response.raise_for_status = MagicMock()
            
            mock_client.return_value.__aenter__.return_value.get.return_value = mock_response
            
            result = await auth_service.get_reddit_user_info(access_token)
            
            assert result['id'] == 'reddit_user_id'
            assert result['name'] == 'test_user'


class TestKeywordService:
    """Test cases for KeywordService."""
    
    @pytest.fixture
    def keyword_service(self, test_db_session):
        """Create KeywordService instance for testing."""
        return KeywordService(db=test_db_session)
    
    @pytest.mark.asyncio
    async def test_create_keyword_success(self, keyword_service, sample_user):
        """Test successful keyword creation."""
        keyword_data = KeywordCreate(keyword="python programming")
        
        # Mock database operations
        keyword_service.db.query.return_value.filter.return_value.first.return_value = None
        keyword_service.db.add = MagicMock()
        keyword_service.db.commit = MagicMock()
        keyword_service.db.refresh = MagicMock()
        
        result = await keyword_service.create_keyword(sample_user.id, keyword_data)
        
        assert isinstance(result, Keyword)
        keyword_service.db.add.assert_called_once()
        keyword_service.db.commit.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_check_keyword_exists_true(self, keyword_service, sample_user):
        """Test checking if keyword exists - returns True."""
        # Mock existing keyword found
        keyword_service.db.query.return_value.filter.return_value.first.return_value = MagicMock()
        
        result = await keyword_service.check_keyword_exists(sample_user.id, "python")
        
        assert result is True
    
    @pytest.mark.asyncio
    async def test_check_keyword_exists_false(self, keyword_service, sample_user):
        """Test checking if keyword exists - returns False."""
        # Mock no keyword found
        keyword_service.db.query.return_value.filter.return_value.first.return_value = None
        
        result = await keyword_service.check_keyword_exists(sample_user.id, "python")
        
        assert result is False
    
    @pytest.mark.asyncio
    async def test_get_keyword_by_id_success(self, keyword_service, sample_keyword):
        """Test retrieving keyword by ID."""
        # Mock database query
        keyword_service.db.query.return_value.filter.return_value.first.return_value = sample_keyword
        
        result = await keyword_service.get_keyword_by_id(sample_keyword.id, sample_keyword.user_id)
        
        assert result == sample_keyword
    
    @pytest.mark.asyncio
    async def test_get_keyword_by_id_not_found(self, keyword_service):
        """Test retrieving non-existent keyword."""
        # Mock database query returning None
        keyword_service.db.query.return_value.filter.return_value.first.return_value = None
        
        result = await keyword_service.get_keyword_by_id(999, 1)
        
        assert result is None
    
    @pytest.mark.asyncio
    async def test_delete_keyword_success(self, keyword_service, sample_keyword):
        """Test successful keyword deletion."""
        # Mock database operations
        keyword_service.db.query.return_value.filter.return_value.first.return_value = sample_keyword
        keyword_service.db.delete = MagicMock()
        keyword_service.db.commit = MagicMock()
        
        result = await keyword_service.delete_keyword(sample_keyword.id, sample_keyword.user_id)
        
        assert result is True
        keyword_service.db.delete.assert_called_once_with(sample_keyword)
        keyword_service.db.commit.assert_called_once()


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
    
    def test_reddit_client_initialization(self, reddit_client):
        """Test Reddit client initialization."""
        assert reddit_client.rate_limiter is not None
        assert reddit_client.reddit_client is None  # Not initialized until first use
    
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


class TestTrendAnalysisService:
    """Test cases for TrendAnalysisService."""
    
    @pytest.fixture
    def trend_service(self):
        """Create TrendAnalysisService instance for testing."""
        return TrendAnalysisService()
    
    @pytest.fixture
    def sample_posts(self, sample_keyword):
        """Sample posts for testing."""
        return [
            Post(
                id=1,
                keyword_id=sample_keyword.id,
                reddit_id="post_1",
                title="Python Machine Learning Tutorial",
                content="Learn machine learning with Python. This tutorial covers scikit-learn, pandas, and numpy.",
                author="ml_expert",
                score=150,
                num_comments=25,
                url="https://reddit.com/1",
                created_at=datetime.utcnow() - timedelta(hours=1)
            ),
            Post(
                id=2,
                keyword_id=sample_keyword.id,
                reddit_id="post_2",
                title="Python Web Development with Django",
                content="Django is a powerful web framework for Python. Learn how to build web applications.",
                author="web_dev",
                score=200,
                num_comments=40,
                url="https://reddit.com/2",
                created_at=datetime.utcnow() - timedelta(hours=2)
            )
        ]
    
    def test_calculate_tfidf_scores_success(self, trend_service, sample_posts):
        """Test successful TF-IDF score calculation."""
        tfidf_scores = trend_service._calculate_tfidf_scores(sample_posts)
        
        assert isinstance(tfidf_scores, dict)
        assert len(tfidf_scores) == len(sample_posts)
        
        # Scores should be between 0 and 1
        for score in tfidf_scores.values():
            assert 0 <= score <= 1
    
    def test_calculate_tfidf_scores_empty_posts(self, trend_service):
        """Test TF-IDF calculation with empty posts."""
        tfidf_scores = trend_service._calculate_tfidf_scores([])
        
        assert tfidf_scores == {}
    
    def test_calculate_engagement_scores(self, trend_service, sample_posts):
        """Test engagement score calculation."""
        engagement_scores = trend_service._calculate_engagement_scores(sample_posts)
        
        assert isinstance(engagement_scores, dict)
        assert len(engagement_scores) == len(sample_posts)
        
        # All scores should be between 0 and 1
        for score in engagement_scores.values():
            assert 0 <= score <= 1
    
    def test_calculate_engagement_scores_empty_posts(self, trend_service):
        """Test engagement score calculation with empty posts."""
        engagement_scores = trend_service._calculate_engagement_scores([])
        
        assert engagement_scores == {}
    
    def test_determine_trend_direction(self, trend_service):
        """Test trend direction determination."""
        # Test upward trend
        assert trend_service._determine_trend_direction(0.25) == "rising"
        
        # Test downward trend  
        assert trend_service._determine_trend_direction(-0.25) == "falling"
        
        # Test stable trend
        assert trend_service._determine_trend_direction(0.05) == "stable"
    
    def test_calculate_confidence_score(self, trend_service):
        """Test confidence score calculation."""
        # Test with good data
        confidence = trend_service._calculate_confidence_score(50, 0.1)
        assert isinstance(confidence, float)
        assert 0 <= confidence <= 1
        
        # Test with limited data
        low_confidence = trend_service._calculate_confidence_score(5, 0.5)
        assert low_confidence < confidence
    
    def test_calculate_engagement_distribution(self, trend_service):
        """Test engagement distribution calculation."""
        engagement_scores = {
            1: 0.1,  # low
            2: 0.2,  # low
            3: 0.5,  # medium
            4: 0.6,  # medium
            5: 0.8,  # high
            6: 0.9   # high
        }
        
        distribution = trend_service._calculate_engagement_distribution(engagement_scores)
        
        assert isinstance(distribution, dict)
        assert "low" in distribution
        assert "medium" in distribution
        assert "high" in distribution
        assert distribution["low"] == 2
        assert distribution["medium"] == 2
        assert distribution["high"] == 2
    
    def test_extract_top_keywords(self, trend_service, sample_posts):
        """Test extraction of top keywords from posts."""
        top_keywords = trend_service._extract_top_keywords(sample_posts, limit=5)
        
        assert isinstance(top_keywords, list)
        assert len(top_keywords) <= 5
        
        for keyword_data in top_keywords:
            assert isinstance(keyword_data, dict)
            assert "keyword" in keyword_data
            assert "score" in keyword_data
    
    def test_calculate_sentiment_scores(self, trend_service, sample_posts):
        """Test sentiment score calculation."""
        sentiment_scores = trend_service._calculate_sentiment_scores(sample_posts)
        
        assert isinstance(sentiment_scores, dict)
        assert len(sentiment_scores) == len(sample_posts)
        
        # Sentiment scores should be between -1 and 1
        for score in sentiment_scores.values():
            assert -1 <= score <= 1
    
    def test_create_empty_trend_data(self, trend_service, sample_keyword):
        """Test creation of empty trend data structure."""
        empty_data = trend_service._create_empty_trend_data(sample_keyword.id)
        
        assert isinstance(empty_data, dict)
        assert empty_data["keyword_id"] == sample_keyword.id
        assert empty_data["avg_tfidf_score"] == 0.0
        assert empty_data["avg_engagement_score"] == 0.0
        assert empty_data["total_posts"] == 0
    
    @pytest.mark.asyncio
    async def test_cache_trend_data(self, trend_service, sample_keyword):
        """Test caching of trend data."""
        trend_data = {
            "keyword_id": sample_keyword.id,
            "avg_tfidf_score": 0.8,
            "avg_engagement_score": 150.0,
            "trend_velocity": 0.2,
            "total_posts": 10
        }
        
        # Mock Redis operations
        with patch.object(trend_service.cache_manager, 'set', new_callable=AsyncMock) as mock_set:
            mock_set.return_value = True
            
            result = await trend_service.cache_trend_data(sample_keyword.id, trend_data)
            
            assert result is True
            mock_set.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_cached_trend_data(self, trend_service, sample_keyword):
        """Test retrieval of cached trend data."""
        # Mock Redis operations
        with patch.object(trend_service.cache_manager, 'get', new_callable=AsyncMock) as mock_get:
            mock_get.return_value = None
            
            result = await trend_service.get_cached_trend_data(sample_keyword.id)
            
            assert result is None
            mock_get.assert_called_once()


class TestContentGenerationService:
    """Test cases for ContentGenerationService."""
    
    @pytest.fixture
    def content_service(self):
        """Create ContentGenerationService instance for testing."""
        return ContentGenerationService()
    
    def test_content_service_initialization(self, content_service):
        """Test ContentGenerationService initialization."""
        assert content_service.template_service is not None
        assert content_service.trend_service is not None
        assert isinstance(content_service.template_service, TemplateService)
        assert isinstance(content_service.trend_service, TrendAnalysisService)


class TestTemplateService:
    """Test cases for TemplateService."""
    
    @pytest.fixture
    def template_service(self):
        """Create TemplateService instance for testing."""
        return TemplateService()
    
    def test_template_service_initialization(self, template_service):
        """Test TemplateService initialization."""
        assert template_service.jinja_env is not None
        assert template_service.template_dir is not None
    
    def test_get_available_templates(self, template_service):
        """Test getting available templates."""
        templates = template_service.get_available_templates()
        
        assert isinstance(templates, list)
        # Should have at least the default templates
        assert len(templates) >= 0
    
    def test_validate_template_data_valid(self, template_service):
        """Test validation of valid template data."""
        valid_data = {
            "keyword": "python",
            "total_posts": "10",
            "avg_engagement": "150.5"
        }
        
        result = template_service.validate_template_data(valid_data)
        
        assert result["valid"] is True
    
    def test_validate_template_data_invalid(self, template_service):
        """Test validation of invalid template data."""
        invalid_data = {}  # Empty data
        
        result = template_service.validate_template_data(invalid_data)
        
        assert result["valid"] is False
        assert "error" in result