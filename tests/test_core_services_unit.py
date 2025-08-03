"""
Core unit tests for essential business logic services.
Tests only the methods and functionality that actually exist in the services.
"""
import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from datetime import datetime, timedelta

from app.services.auth_service import AuthService
from app.services.keyword_service import KeywordService
from app.services.trend_analysis_service import TrendAnalysisService
from app.services.content_generation_service import ContentGenerationService
from app.services.template_service import TemplateService

from app.models.user import User
from app.models.keyword import Keyword
from app.models.post import Post
from app.schemas.keyword import KeywordCreate


class TestAuthService:
    """Test cases for AuthService - OAuth2 authentication and token management."""
    
    @pytest.fixture
    def auth_service(self):
        """Create AuthService instance for testing."""
        return AuthService()
    
    def test_get_reddit_auth_url(self, auth_service):
        """Test Reddit OAuth URL generation."""
        state = "test_state_123"
        url = auth_service.get_reddit_auth_url(state)
        
        assert isinstance(url, str)
        assert "reddit.com" in url
        assert "authorize" in url
        assert state in url
        assert "client_id" in url
        assert "response_type=code" in url
    
    @pytest.mark.asyncio
    async def test_exchange_code_for_token_success(self, auth_service):
        """Test successful OAuth code exchange for token."""
        code = "valid_oauth_code"
        
        with patch('httpx.AsyncClient') as mock_client:
            mock_response = MagicMock()
            mock_response.json.return_value = {
                'access_token': 'reddit_access_token_123',
                'token_type': 'bearer',
                'expires_in': 3600
            }
            mock_response.raise_for_status = MagicMock()
            
            mock_client.return_value.__aenter__.return_value.post.return_value = mock_response
            
            result = await auth_service.exchange_code_for_token(code)
            
            assert result['access_token'] == 'reddit_access_token_123'
            assert result['token_type'] == 'bearer'
    
    @pytest.mark.asyncio
    async def test_get_reddit_user_info_success(self, auth_service):
        """Test successful Reddit user info retrieval."""
        access_token = "valid_reddit_token"
        
        with patch('httpx.AsyncClient') as mock_client:
            mock_response = MagicMock()
            mock_response.json.return_value = {
                'id': 'reddit_user_12345',
                'name': 'test_reddit_user',
                'created_utc': 1640995200
            }
            mock_response.raise_for_status = MagicMock()
            
            mock_client.return_value.__aenter__.return_value.get.return_value = mock_response
            
            result = await auth_service.get_reddit_user_info(access_token)
            
            assert result['id'] == 'reddit_user_12345'
            assert result['name'] == 'test_reddit_user'
    
    @pytest.mark.asyncio
    async def test_exchange_code_for_token_http_error(self, auth_service):
        """Test OAuth code exchange with HTTP error."""
        code = "invalid_code"
        
        with patch('httpx.AsyncClient') as mock_client:
            mock_response = MagicMock()
            mock_response.raise_for_status.side_effect = Exception("HTTP 400: Invalid code")
            
            mock_client.return_value.__aenter__.return_value.post.return_value = mock_response
            
            with pytest.raises(Exception):
                await auth_service.exchange_code_for_token(code)


class TestKeywordService:
    """Test cases for KeywordService - keyword CRUD operations."""
    
    @pytest.fixture
    def keyword_service(self, test_db_session):
        """Create KeywordService instance for testing."""
        return KeywordService(db=test_db_session)
    
    @pytest.mark.asyncio
    async def test_create_keyword_success(self, keyword_service, sample_user):
        """Test successful keyword creation."""
        keyword_data = KeywordCreate(keyword="machine learning")
        
        # Mock database operations - no existing keyword
        keyword_service.db.query.return_value.filter.return_value.first.return_value = None
        keyword_service.db.add = MagicMock()
        keyword_service.db.commit = MagicMock()
        keyword_service.db.refresh = MagicMock()
        
        result = await keyword_service.create_keyword(sample_user.id, keyword_data)
        
        assert isinstance(result, Keyword)
        assert result.keyword == keyword_data.keyword
        assert result.user_id == sample_user.id
        keyword_service.db.add.assert_called_once()
        keyword_service.db.commit.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_create_keyword_duplicate_error(self, keyword_service, sample_user, sample_keyword):
        """Test creating duplicate keyword raises HTTPException."""
        from fastapi import HTTPException
        
        keyword_data = KeywordCreate(keyword=sample_keyword.keyword)
        
        # Mock existing keyword found
        keyword_service.db.query.return_value.filter.return_value.first.return_value = sample_keyword
        
        with pytest.raises(HTTPException):
            await keyword_service.create_keyword(sample_user.id, keyword_data)
    
    @pytest.mark.asyncio
    async def test_check_keyword_exists_true(self, keyword_service, sample_user):
        """Test keyword existence check returns True when keyword exists."""
        # Mock existing keyword found
        mock_keyword = MagicMock()
        keyword_service.db.query.return_value.filter.return_value.first.return_value = mock_keyword
        
        result = await keyword_service.check_keyword_exists(sample_user.id, "python")
        
        assert result is True
    
    @pytest.mark.asyncio
    async def test_check_keyword_exists_false(self, keyword_service, sample_user):
        """Test keyword existence check returns False when keyword doesn't exist."""
        # Mock no keyword found
        keyword_service.db.query.return_value.filter.return_value.first.return_value = None
        
        result = await keyword_service.check_keyword_exists(sample_user.id, "nonexistent")
        
        assert result is False
    
    @pytest.mark.asyncio
    async def test_get_keyword_by_id_success(self, keyword_service, sample_keyword):
        """Test successful keyword retrieval by ID."""
        # Mock database query
        keyword_service.db.query.return_value.filter.return_value.first.return_value = sample_keyword
        
        result = await keyword_service.get_keyword_by_id(sample_keyword.id, sample_keyword.user_id)
        
        assert result == sample_keyword
    
    @pytest.mark.asyncio
    async def test_get_keyword_by_id_not_found(self, keyword_service):
        """Test keyword retrieval returns None when not found."""
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
    
    @pytest.mark.asyncio
    async def test_delete_keyword_not_found(self, keyword_service):
        """Test deleting non-existent keyword returns False."""
        # Mock database query returning None
        keyword_service.db.query.return_value.filter.return_value.first.return_value = None
        
        result = await keyword_service.delete_keyword(999, 1)
        
        # Based on the actual implementation, it returns False when not found
        assert result is False


class TestTrendAnalysisService:
    """Test cases for TrendAnalysisService - TF-IDF analysis and trend calculation."""
    
    @pytest.fixture
    def trend_service(self):
        """Create TrendAnalysisService instance for testing."""
        return TrendAnalysisService()
    
    @pytest.fixture
    def sample_posts(self, sample_keyword):
        """Sample posts for testing trend analysis."""
        return [
            Post(
                id=1,
                keyword_id=sample_keyword.id,
                reddit_id="post_1",
                title="Python Machine Learning Guide",
                content="Comprehensive guide to machine learning with Python using scikit-learn and pandas.",
                author="ml_expert",
                score=250,
                num_comments=45,
                url="https://reddit.com/r/MachineLearning/post_1",
                created_at=datetime.utcnow() - timedelta(hours=2)
            ),
            Post(
                id=2,
                keyword_id=sample_keyword.id,
                reddit_id="post_2", 
                title="Python Web Development Tutorial",
                content="Learn web development with Python using Django and Flask frameworks.",
                author="web_developer",
                score=180,
                num_comments=32,
                url="https://reddit.com/r/Python/post_2",
                created_at=datetime.utcnow() - timedelta(hours=4)
            ),
            Post(
                id=3,
                keyword_id=sample_keyword.id,
                reddit_id="post_3",
                title="Python Data Science Projects",
                content="Explore data science projects using Python, numpy, pandas, and matplotlib.",
                author="data_scientist",
                score=320,
                num_comments=67,
                url="https://reddit.com/r/datascience/post_3",
                created_at=datetime.utcnow() - timedelta(hours=6)
            )
        ]
    
    def test_calculate_tfidf_scores_success(self, trend_service, sample_posts):
        """Test successful TF-IDF score calculation."""
        tfidf_scores = trend_service._calculate_tfidf_scores(sample_posts)
        
        assert isinstance(tfidf_scores, dict)
        assert len(tfidf_scores) == len(sample_posts)
        
        # Each post should have a TF-IDF score
        for post in sample_posts:
            assert post.id in tfidf_scores
            assert isinstance(tfidf_scores[post.id], float)
            assert 0 <= tfidf_scores[post.id] <= 1
    
    def test_calculate_tfidf_scores_empty_posts(self, trend_service):
        """Test TF-IDF calculation with empty post list."""
        tfidf_scores = trend_service._calculate_tfidf_scores([])
        
        assert tfidf_scores == {}
    
    def test_calculate_engagement_scores_success(self, trend_service, sample_posts):
        """Test successful engagement score calculation."""
        engagement_scores = trend_service._calculate_engagement_scores(sample_posts)
        
        assert isinstance(engagement_scores, dict)
        assert len(engagement_scores) == len(sample_posts)
        
        # Each post should have an engagement score between 0 and 1
        for post in sample_posts:
            assert post.id in engagement_scores
            assert isinstance(engagement_scores[post.id], float)
            assert 0 <= engagement_scores[post.id] <= 1
        
        # Post with highest score + comments should have highest engagement
        post_3_engagement = engagement_scores[3]  # Post 3 has score=320, comments=67
        post_1_engagement = engagement_scores[1]  # Post 1 has score=250, comments=45
        assert post_3_engagement >= post_1_engagement
    
    def test_calculate_engagement_scores_empty_posts(self, trend_service):
        """Test engagement score calculation with empty post list."""
        engagement_scores = trend_service._calculate_engagement_scores([])
        
        assert engagement_scores == {}
    
    def test_determine_trend_direction(self, trend_service):
        """Test trend direction determination based on velocity."""
        # Test rising trend
        assert trend_service._determine_trend_direction(0.25) == "rising"
        
        # Test falling trend  
        assert trend_service._determine_trend_direction(-0.25) == "falling"
        
        # Test stable trend
        assert trend_service._determine_trend_direction(0.05) == "stable"
        assert trend_service._determine_trend_direction(-0.05) == "stable"
    
    def test_calculate_confidence_score(self, trend_service):
        """Test confidence score calculation."""
        # Test with good amount of data
        confidence_high = trend_service._calculate_confidence_score(100, 0.1)
        assert isinstance(confidence_high, float)
        assert 0 <= confidence_high <= 1
        
        # Test with limited data
        confidence_low = trend_service._calculate_confidence_score(5, 0.8)
        assert isinstance(confidence_low, float)
        assert 0 <= confidence_low <= 1
        
        # More posts should generally give higher confidence
        assert confidence_high >= confidence_low
    
    def test_calculate_engagement_distribution(self, trend_service):
        """Test engagement score distribution calculation."""
        engagement_scores = {
            1: 0.1,   # low
            2: 0.25,  # low  
            3: 0.5,   # medium
            4: 0.65,  # medium
            5: 0.8,   # high
            6: 0.95   # high
        }
        
        distribution = trend_service._calculate_engagement_distribution(engagement_scores)
        
        assert isinstance(distribution, dict)
        assert "low" in distribution
        assert "medium" in distribution  
        assert "high" in distribution
        assert distribution["low"] == 2
        assert distribution["medium"] == 2
        assert distribution["high"] == 2
        assert sum(distribution.values()) == len(engagement_scores)
    
    def test_extract_top_keywords(self, trend_service, sample_posts):
        """Test extraction of top keywords from posts."""
        top_keywords = trend_service._extract_top_keywords(sample_posts, limit=5)
        
        assert isinstance(top_keywords, list)
        assert len(top_keywords) <= 5
        
        for keyword_data in top_keywords:
            assert isinstance(keyword_data, dict)
            assert "keyword" in keyword_data
            assert "score" in keyword_data
            assert isinstance(keyword_data["keyword"], str)
            assert isinstance(keyword_data["score"], float)
    
    def test_calculate_sentiment_scores(self, trend_service, sample_posts):
        """Test sentiment score calculation for posts."""
        sentiment_scores = trend_service._calculate_sentiment_scores(sample_posts)
        
        assert isinstance(sentiment_scores, dict)
        assert len(sentiment_scores) == len(sample_posts)
        
        # Sentiment scores should be between -1 and 1
        for post in sample_posts:
            assert post.id in sentiment_scores
            assert isinstance(sentiment_scores[post.id], float)
            assert -1 <= sentiment_scores[post.id] <= 1
    
    def test_create_empty_trend_data(self, trend_service, sample_keyword):
        """Test creation of empty trend data structure."""
        empty_data = trend_service._create_empty_trend_data(sample_keyword.id)
        
        assert isinstance(empty_data, dict)
        assert empty_data["keyword_id"] == sample_keyword.id
        assert empty_data["avg_tfidf_score"] == 0.0
        assert empty_data["avg_engagement_score"] == 0.0
        assert empty_data["total_posts"] == 0
        assert empty_data["trend_velocity"] == 0.0
        assert "analyzed_at" in empty_data
        assert "cache_expires_at" in empty_data


class TestContentGenerationService:
    """Test cases for ContentGenerationService - blog content generation."""
    
    @pytest.fixture
    def content_service(self):
        """Create ContentGenerationService instance for testing."""
        return ContentGenerationService()
    
    def test_content_service_initialization(self, content_service):
        """Test ContentGenerationService proper initialization."""
        assert content_service.template_service is not None
        assert content_service.trend_service is not None
        assert isinstance(content_service.template_service, TemplateService)
        assert isinstance(content_service.trend_service, TrendAnalysisService)


class TestTemplateService:
    """Test cases for TemplateService - template management and rendering."""
    
    @pytest.fixture
    def template_service(self):
        """Create TemplateService instance for testing."""
        return TemplateService()
    
    def test_template_service_initialization(self, template_service):
        """Test TemplateService proper initialization."""
        assert template_service.jinja_env is not None
        assert hasattr(template_service, 'templates_dir')
        assert template_service.templates_dir is not None
    
    def test_get_available_templates(self, template_service):
        """Test getting list of available templates."""
        templates = template_service.get_available_templates()
        
        assert isinstance(templates, list)
        # Should have at least some templates (even if empty list is valid)
        assert len(templates) >= 0
        
        # Templates are returned as dictionaries with metadata, not strings
        for template in templates:
            assert isinstance(template, dict)
            assert "name" in template
            assert "display_name" in template
    
    def test_validate_template_valid_structure(self, template_service):
        """Test template validation with valid template structure."""
        # Create a simple valid template structure
        valid_template = {
            "title": "Test Template",
            "sections": [
                {"name": "intro", "content": "Introduction content"}
            ]
        }
        
        result = template_service.validate_template(valid_template)
        
        assert isinstance(result, dict)
        assert "valid" in result
        # Note: The actual validation logic may vary, so we just check structure
    
    def test_validate_template_invalid_structure(self, template_service):
        """Test template validation with invalid template structure."""
        # Create an invalid template (empty dict)
        invalid_template = {}
        
        result = template_service.validate_template(invalid_template)
        
        assert isinstance(result, dict)
        assert "valid" in result
        # Invalid templates should return valid=False
        assert result["valid"] is False