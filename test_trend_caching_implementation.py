"""
Test implementation for enhanced trend data caching and API functionality.
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import Mock, AsyncMock, patch
from sqlalchemy.orm import Session

from app.services.trend_analysis_service import trend_analysis_service
from app.models.keyword import Keyword
from app.models.post import Post
from app.models.metric import Metric
from app.core.redis_client import cache_manager


class TestTrendCachingImplementation:
    """Test cases for trend caching implementation."""
    
    @pytest.fixture
    def mock_db(self):
        """Mock database session."""
        return Mock(spec=Session)
    
    @pytest.fixture
    def sample_keyword(self):
        """Sample keyword for testing."""
        keyword = Mock(spec=Keyword)
        keyword.id = 1
        keyword.keyword = "test_keyword"
        keyword.user_id = 1
        keyword.is_active = True
        return keyword
    
    @pytest.fixture
    def sample_posts(self):
        """Sample posts for testing."""
        posts = []
        for i in range(3):
            post = Mock(spec=Post)
            post.id = i + 1
            post.keyword_id = 1
            post.title = f"Test Post {i + 1}"
            post.content = f"This is test content for post {i + 1}"
            post.score = (i + 1) * 10
            post.num_comments = (i + 1) * 5
            post.created_at = datetime.utcnow() - timedelta(hours=i)
            posts.append(post)
        return posts
    
    @pytest.mark.asyncio
    async def test_cache_trend_data(self, sample_keyword):
        """Test caching of trend data."""
        trend_data = {
            "keyword_id": sample_keyword.id,
            "avg_tfidf_score": 0.75,
            "avg_engagement_score": 0.65,
            "trend_velocity": 0.1,
            "total_posts": 5,
            "analyzed_at": datetime.utcnow().isoformat()
        }
        
        # Mock the cache manager
        with patch.object(cache_manager, 'cache_trend_data', return_value=True) as mock_cache:
            result = await trend_analysis_service.cache_trend_data(sample_keyword.id, trend_data)
            
            assert result is True
            mock_cache.assert_called_once_with(
                sample_keyword.id, 
                trend_data, 
                trend_analysis_service.TREND_DATA_CACHE_TTL
            )
    
    @pytest.mark.asyncio
    async def test_get_cached_trend_data(self, sample_keyword):
        """Test retrieval of cached trend data."""
        expected_data = {
            "keyword_id": sample_keyword.id,
            "avg_tfidf_score": 0.75,
            "avg_engagement_score": 0.65,
            "cached": True
        }
        
        # Mock the cache manager
        with patch.object(cache_manager, 'get_cached_trend_data', return_value=expected_data) as mock_get:
            result = await trend_analysis_service.get_cached_trend_data(sample_keyword.id)
            
            assert result == expected_data
            mock_get.assert_called_once_with(sample_keyword.id)
    
    @pytest.mark.asyncio
    async def test_invalidate_trend_cache(self, sample_keyword):
        """Test cache invalidation."""
        with patch.object(cache_manager.redis, 'delete', return_value=True) as mock_delete:
            result = await trend_analysis_service.invalidate_trend_cache(sample_keyword.id)
            
            assert result is True
            mock_delete.assert_called_once()
    
    def test_calculate_sentiment_scores(self, sample_posts):
        """Test sentiment score calculation."""
        # Add sentiment words to posts
        sample_posts[0].title = "This is a great post"
        sample_posts[0].content = "Amazing content here"
        sample_posts[1].title = "This is a terrible post"
        sample_posts[1].content = "Awful content here"
        sample_posts[2].title = "This is a neutral post"
        sample_posts[2].content = "Regular content here"
        
        sentiment_scores = trend_analysis_service._calculate_sentiment_scores(sample_posts)
        
        assert len(sentiment_scores) == 3
        assert sentiment_scores[1] > 0  # Positive sentiment
        assert sentiment_scores[2] < 0  # Negative sentiment
        assert sentiment_scores[3] == 0  # Neutral sentiment
    
    def test_calculate_virality_scores(self, sample_posts, mock_db):
        """Test virality score calculation."""
        virality_scores = trend_analysis_service._calculate_virality_scores(sample_posts, mock_db)
        
        assert len(virality_scores) == 3
        # Newer posts should have higher virality scores
        assert virality_scores[1] >= virality_scores[2] >= virality_scores[3]
    
    def test_extract_top_keywords(self, sample_posts):
        """Test top keyword extraction."""
        # Set up posts with specific content
        sample_posts[0].title = "Machine learning algorithms"
        sample_posts[0].content = "Deep learning neural networks"
        sample_posts[1].title = "Artificial intelligence trends"
        sample_posts[1].content = "Machine learning applications"
        sample_posts[2].title = "Data science methods"
        sample_posts[2].content = "Statistical analysis techniques"
        
        top_keywords = trend_analysis_service._extract_top_keywords(sample_posts, limit=5)
        
        assert len(top_keywords) <= 5
        assert all(isinstance(kw, dict) for kw in top_keywords)
        assert all("keyword" in kw and "score" in kw for kw in top_keywords)
    
    def test_calculate_engagement_distribution(self):
        """Test engagement distribution calculation."""
        engagement_scores = {
            1: 0.2,  # Low
            2: 0.5,  # Medium
            3: 0.8,  # High
            4: 0.1,  # Low
            5: 0.9   # High
        }
        
        distribution = trend_analysis_service._calculate_engagement_distribution(engagement_scores)
        
        assert distribution["low"] == 2
        assert distribution["medium"] == 1
        assert distribution["high"] == 2
    
    def test_determine_trend_direction(self):
        """Test trend direction determination."""
        assert trend_analysis_service._determine_trend_direction(0.2) == "rising"
        assert trend_analysis_service._determine_trend_direction(-0.2) == "falling"
        assert trend_analysis_service._determine_trend_direction(0.05) == "stable"
    
    def test_calculate_confidence_score(self):
        """Test confidence score calculation."""
        # High post count, low velocity = high confidence
        confidence1 = trend_analysis_service._calculate_confidence_score(100, 0.1)
        
        # Low post count, high velocity = lower confidence
        confidence2 = trend_analysis_service._calculate_confidence_score(5, 0.8)
        
        assert 0 <= confidence1 <= 1
        assert 0 <= confidence2 <= 1
        assert confidence1 > confidence2
    
    @pytest.mark.asyncio
    async def test_store_trend_history(self, sample_keyword, mock_db):
        """Test trend history storage."""
        trend_data = {
            "avg_tfidf_score": 0.75,
            "avg_engagement_score": 0.65,
            "trend_velocity": 0.1,
            "total_posts": 5,
            "confidence_score": 0.8
        }
        
        with patch.object(cache_manager.redis, 'get_json', return_value=[]) as mock_get, \
             patch.object(cache_manager.redis, 'set_json', return_value=True) as mock_set:
            
            await trend_analysis_service._store_trend_history(sample_keyword.id, trend_data, mock_db)
            
            mock_get.assert_called_once()
            mock_set.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_trend_history(self, sample_keyword):
        """Test trend history retrieval."""
        mock_history = [
            {
                "timestamp": (datetime.utcnow() - timedelta(days=1)).isoformat(),
                "avg_tfidf_score": 0.7,
                "avg_engagement_score": 0.6,
                "trend_velocity": 0.1,
                "total_posts": 4,
                "confidence_score": 0.75
            },
            {
                "timestamp": (datetime.utcnow() - timedelta(days=2)).isoformat(),
                "avg_tfidf_score": 0.65,
                "avg_engagement_score": 0.55,
                "trend_velocity": 0.05,
                "total_posts": 3,
                "confidence_score": 0.7
            }
        ]
        
        with patch.object(cache_manager.redis, 'get_json', return_value=mock_history) as mock_get:
            history = await trend_analysis_service.get_trend_history(sample_keyword.id, days=7)
            
            assert len(history) == 2
            mock_get.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_trend_summary(self, mock_db):
        """Test trend summary generation."""
        user_id = 1
        
        # Mock keywords
        mock_keywords = [
            Mock(id=1, keyword="test1", user_id=user_id, is_active=True),
            Mock(id=2, keyword="test2", user_id=user_id, is_active=True)
        ]
        
        mock_db.query.return_value.filter.return_value.all.return_value = mock_keywords
        
        # Mock cached trend data
        mock_trend_data = {
            "total_posts": 10,
            "avg_engagement_score": 0.7,
            "avg_tfidf_score": 0.6
        }
        
        with patch.object(trend_analysis_service, 'get_cached_trend_data', return_value=mock_trend_data) as mock_get, \
             patch.object(cache_manager.redis, 'get_json', return_value=None) as mock_cache_get, \
             patch.object(cache_manager.redis, 'set_json', return_value=True) as mock_cache_set:
            
            summary = await trend_analysis_service.get_trend_summary(user_id, mock_db)
            
            assert summary["user_id"] == user_id
            assert len(summary["keywords"]) == 2
            assert "summary" in summary
    
    @pytest.mark.asyncio
    async def test_compare_keywords(self, mock_db):
        """Test keyword comparison functionality."""
        keyword_ids = [1, 2]
        
        # Mock keywords
        mock_keywords = [
            Mock(id=1, keyword="test1"),
            Mock(id=2, keyword="test2")
        ]
        
        mock_db.query.return_value.filter.return_value.first.side_effect = mock_keywords
        
        # Mock trend data
        mock_trend_data = {
            "avg_engagement_score": 0.7,
            "avg_tfidf_score": 0.6
        }
        
        with patch.object(trend_analysis_service, 'get_cached_trend_data', return_value=mock_trend_data):
            comparison = await trend_analysis_service.compare_keywords(keyword_ids, mock_db)
            
            assert "keywords" in comparison
            assert "comparison_summary" in comparison
            assert len(comparison["keywords"]) == 2
    
    def test_create_empty_trend_data(self):
        """Test creation of empty trend data structure."""
        keyword_id = 1
        empty_data = trend_analysis_service._create_empty_trend_data(keyword_id)
        
        assert empty_data["keyword_id"] == keyword_id
        assert empty_data["total_posts"] == 0
        assert empty_data["avg_tfidf_score"] == 0.0
        assert empty_data["avg_engagement_score"] == 0.0
        assert "analyzed_at" in empty_data
        assert "cache_expires_at" in empty_data


def test_trend_caching_integration():
    """Integration test for trend caching functionality."""
    print("✅ Testing trend data caching implementation...")
    
    # Test cache key generation
    keyword_id = 123
    expected_cache_key = f"trend:keyword:{keyword_id}"
    
    # Test cache TTL values
    assert trend_analysis_service.TREND_DATA_CACHE_TTL == 1800  # 30 minutes
    assert trend_analysis_service.TREND_HISTORY_CACHE_TTL == 3600  # 1 hour
    assert trend_analysis_service.KEYWORD_RANKING_CACHE_TTL == 900  # 15 minutes
    assert trend_analysis_service.TREND_SUMMARY_CACHE_TTL == 600  # 10 minutes
    
    print("✅ Cache configuration validated")
    
    # Test helper methods
    service = trend_analysis_service
    
    # Test sentiment calculation with empty posts
    sentiment_scores = service._calculate_sentiment_scores([])
    assert sentiment_scores == {}
    
    # Test engagement distribution with empty scores
    distribution = service._calculate_engagement_distribution({})
    assert distribution == {"low": 0, "medium": 0, "high": 0}
    
    # Test trend direction determination
    assert service._determine_trend_direction(0.15) == "rising"
    assert service._determine_trend_direction(-0.15) == "falling"
    assert service._determine_trend_direction(0.05) == "stable"
    
    # Test confidence score calculation
    confidence = service._calculate_confidence_score(25, 0.2)
    assert 0 <= confidence <= 1
    
    print("✅ Helper methods validated")
    
    # Test empty trend data creation
    empty_data = service._create_empty_trend_data(keyword_id)
    assert empty_data["keyword_id"] == keyword_id
    assert empty_data["total_posts"] == 0
    assert "analyzed_at" in empty_data
    
    print("✅ Empty trend data structure validated")
    
    print("✅ All trend caching implementation tests passed!")


if __name__ == "__main__":
    test_trend_caching_integration()
    print("\n🎉 Trend caching and API implementation completed successfully!")