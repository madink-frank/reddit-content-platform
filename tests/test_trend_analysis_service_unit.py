"""
Unit tests for Trend Analysis Service.
"""
import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from datetime import datetime, timedelta
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer

from app.services.trend_analysis_service import TrendAnalysisService
from app.models.post import Post
from app.models.metric import Metric
from app.schemas.trend import TrendMetrics, KeywordRanking


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
            ),
            Post(
                id=3,
                keyword_id=sample_keyword.id,
                reddit_id="post_3",
                title="Python Data Science Projects",
                content="Explore data science projects using Python, pandas, matplotlib, and seaborn.",
                author="data_scientist",
                score=300,
                num_comments=60,
                url="https://reddit.com/3",
                created_at=datetime.utcnow() - timedelta(hours=3)
            )
        ]
    
    def test_calculate_tfidf_scores_success(self, trend_service, sample_posts):
        """Test successful TF-IDF score calculation."""
        tfidf_scores = trend_service._calculate_tfidf_scores(sample_posts)
        
        assert isinstance(tfidf_scores, dict)
        assert len(tfidf_scores) > 0
        
        # Should have scores for each post
        assert len(tfidf_scores) == len(sample_posts)
        
        # Scores should be between 0 and 1
        for score in tfidf_scores.values():
            assert 0 <= score <= 1
    
    def test_calculate_tfidf_scores_empty_posts(self, trend_service):
        """Test TF-IDF calculation with empty posts."""
        tfidf_scores = trend_service._calculate_tfidf_scores([])
        
        assert tfidf_scores == {}
    
    def test_calculate_tfidf_scores_single_post(self, trend_service, sample_posts):
        """Test TF-IDF calculation with single post."""
        single_post = [sample_posts[0]]
        
        tfidf_scores = trend_service._calculate_tfidf_scores(single_post)
        
        assert isinstance(tfidf_scores, dict)
        assert len(tfidf_scores) == 1
    
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
    
    def test_calculate_trend_velocity(self, trend_service, test_db_session, sample_keyword):
        """Test trend velocity calculation."""
        # Mock database session
        test_db_session.query.return_value.filter.return_value.order_by.return_value.limit.return_value.all.return_value = []
        
        velocity = trend_service._calculate_trend_velocity(sample_keyword.id, test_db_session)
        
        assert isinstance(velocity, float)
        assert velocity >= 0  # Should be non-negative
    
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
    
    def test_calculate_virality_scores(self, trend_service, sample_posts, test_db_session):
        """Test virality score calculation."""
        # Mock database session
        test_db_session.query.return_value.filter.return_value.order_by.return_value.limit.return_value.all.return_value = []
        
        virality_scores = trend_service._calculate_virality_scores(sample_posts, test_db_session)
        
        assert isinstance(virality_scores, dict)
        assert len(virality_scores) == len(sample_posts)
        
        # Virality scores should be non-negative
        for score in virality_scores.values():
            assert score >= 0
    
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
    
    @pytest.mark.asyncio
    async def test_invalidate_trend_cache(self, trend_service, sample_keyword):
        """Test trend cache invalidation."""
        # Mock Redis operations
        with patch.object(trend_service.cache_manager, 'delete', new_callable=AsyncMock) as mock_delete:
            mock_delete.return_value = True
            
            result = await trend_service.invalidate_trend_cache(sample_keyword.id)
            
            assert result is True
            mock_delete.assert_called_once()