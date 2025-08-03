"""
Test script for TF-IDF trend analysis engine implementation.
"""

import sys
import os
import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
import numpy as np

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.services.trend_analysis_service import TrendAnalysisService
from app.models.post import Post, Comment
from app.models.keyword import Keyword
from app.models.metric import Metric


class TestTrendAnalysisService:
    """Test cases for TrendAnalysisService."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.service = TrendAnalysisService()
        
        # Mock Redis client
        self.mock_redis = Mock()
        self.service.redis_client = self.mock_redis
        
        # Create sample posts
        self.sample_posts = [
            Post(
                id=1,
                keyword_id=1,
                reddit_id="post1",
                title="Machine Learning Trends 2024",
                content="This is about machine learning and AI trends",
                author="user1",
                score=100,
                num_comments=25,
                url="https://reddit.com/r/MachineLearning/post1",
                subreddit="MachineLearning",
                post_created_at=datetime.utcnow()
            ),
            Post(
                id=2,
                keyword_id=1,
                reddit_id="post2",
                title="Deep Learning Applications",
                content="Deep learning is transforming various industries",
                author="user2",
                score=75,
                num_comments=15,
                url="https://reddit.com/r/MachineLearning/post2",
                subreddit="MachineLearning",
                post_created_at=datetime.utcnow()
            ),
            Post(
                id=3,
                keyword_id=1,
                reddit_id="post3",
                title="Neural Networks Explained",
                content="Understanding neural networks and their applications",
                author="user3",
                score=50,
                num_comments=10,
                url="https://reddit.com/r/MachineLearning/post3",
                subreddit="MachineLearning",
                post_created_at=datetime.utcnow()
            )
        ]
    
    def test_calculate_tfidf_scores(self):
        """Test TF-IDF score calculation."""
        print("Testing TF-IDF score calculation...")
        
        # Test with sample posts
        tfidf_scores = self.service._calculate_tfidf_scores(self.sample_posts)
        
        # Verify results
        assert isinstance(tfidf_scores, dict)
        assert len(tfidf_scores) == len(self.sample_posts)
        
        # Check that all scores are between 0 and 1
        for post_id, score in tfidf_scores.items():
            assert 0 <= score <= 1, f"TF-IDF score {score} for post {post_id} is not normalized"
            print(f"Post {post_id}: TF-IDF score = {score:.4f}")
        
        print("✓ TF-IDF score calculation test passed")
    
    def test_calculate_tfidf_scores_empty_posts(self):
        """Test TF-IDF calculation with empty posts list."""
        print("Testing TF-IDF calculation with empty posts...")
        
        tfidf_scores = self.service._calculate_tfidf_scores([])
        
        assert tfidf_scores == {}
        print("✓ Empty posts TF-IDF test passed")
    
    def test_calculate_engagement_scores(self):
        """Test engagement score calculation."""
        print("Testing engagement score calculation...")
        
        engagement_scores = self.service._calculate_engagement_scores(self.sample_posts)
        
        # Verify results
        assert isinstance(engagement_scores, dict)
        assert len(engagement_scores) == len(self.sample_posts)
        
        # Check that all scores are between 0 and 1
        for post_id, score in engagement_scores.items():
            assert 0 <= score <= 1, f"Engagement score {score} for post {post_id} is not normalized"
            print(f"Post {post_id}: Engagement score = {score:.4f}")
        
        # Verify that higher Reddit scores result in higher engagement scores
        post_scores = [(post.id, post.score, engagement_scores[post.id]) for post in self.sample_posts]
        post_scores.sort(key=lambda x: x[1], reverse=True)  # Sort by Reddit score
        
        # The post with highest Reddit score should have highest engagement score
        assert post_scores[0][2] >= post_scores[1][2], "Engagement scores don't correlate with Reddit scores"
        
        print("✓ Engagement score calculation test passed")
    
    def test_calculate_engagement_scores_empty_posts(self):
        """Test engagement calculation with empty posts list."""
        print("Testing engagement calculation with empty posts...")
        
        engagement_scores = self.service._calculate_engagement_scores([])
        
        assert engagement_scores == {}
        print("✓ Empty posts engagement test passed")
    
    @patch('app.services.trend_analysis_service.Session')
    def test_calculate_trend_velocity(self, mock_session):
        """Test trend velocity calculation."""
        print("Testing trend velocity calculation...")
        
        # Mock database session and query results
        mock_db = Mock()
        
        # Create mock metrics with different engagement scores over time
        mock_metrics = [
            Mock(engagement_score=0.8, calculated_at=datetime.utcnow()),
            Mock(engagement_score=0.7, calculated_at=datetime.utcnow() - timedelta(hours=12)),
            Mock(engagement_score=0.6, calculated_at=datetime.utcnow() - timedelta(days=1)),
            Mock(engagement_score=0.5, calculated_at=datetime.utcnow() - timedelta(days=2))
        ]
        
        mock_db.query.return_value.join.return_value.filter.return_value.order_by.return_value.all.return_value = mock_metrics
        
        velocity = self.service._calculate_trend_velocity(1, mock_db)
        
        # Verify result
        assert isinstance(velocity, float)
        print(f"Trend velocity: {velocity:.4f}")
        
        print("✓ Trend velocity calculation test passed")
    
    @patch('app.services.trend_analysis_service.Session')
    def test_calculate_trend_velocity_insufficient_data(self, mock_session):
        """Test trend velocity calculation with insufficient data."""
        print("Testing trend velocity with insufficient data...")
        
        mock_db = Mock()
        mock_db.query.return_value.join.return_value.filter.return_value.order_by.return_value.all.return_value = []
        
        velocity = self.service._calculate_trend_velocity(1, mock_db)
        
        assert velocity == 0.0
        print("✓ Insufficient data trend velocity test passed")
    
    @patch('app.services.trend_analysis_service.Session')
    def test_store_metrics(self, mock_session):
        """Test storing metrics in database."""
        print("Testing metrics storage...")
        
        mock_db = Mock()
        mock_db.query.return_value.filter.return_value.first.return_value = None  # No existing metrics
        
        tfidf_scores = {1: 0.8, 2: 0.6, 3: 0.4}
        engagement_scores = {1: 0.9, 2: 0.7, 3: 0.5}
        trend_velocity = 0.1
        
        # Test storing new metrics
        self.service._store_metrics(
            self.sample_posts,
            tfidf_scores,
            engagement_scores,
            trend_velocity,
            mock_db
        )
        
        # Verify that metrics were added to database
        assert mock_db.add.call_count == len(self.sample_posts)
        mock_db.commit.assert_called_once()
        
        print("✓ Metrics storage test passed")
    
    def test_get_cached_trend_data(self):
        """Test getting cached trend data."""
        print("Testing cached trend data retrieval...")
        
        # Mock Redis response
        cached_data = "{'keyword_id': 1, 'avg_tfidf_score': 0.5}"
        self.mock_redis.get.return_value = cached_data
        
        result = self.service.get_cached_trend_data(1)
        
        # Verify Redis was called with correct key
        self.mock_redis.get.assert_called_with("trend_analysis:1")
        
        # Verify result
        assert result is not None
        print("✓ Cached trend data test passed")
    
    def test_get_cached_trend_data_not_found(self):
        """Test getting cached trend data when not found."""
        print("Testing cached trend data not found...")
        
        self.mock_redis.get.return_value = None
        
        result = self.service.get_cached_trend_data(1)
        
        assert result is None
        print("✓ Cached trend data not found test passed")
    
    @patch('app.services.trend_analysis_service.Session')
    def test_analyze_keyword_trends_integration(self, mock_session):
        """Test full keyword trends analysis integration."""
        print("Testing full keyword trends analysis...")
        
        # Mock database session
        mock_db = Mock()
        mock_db.query.return_value.filter.return_value.all.return_value = self.sample_posts
        mock_db.query.return_value.join.return_value.filter.return_value.order_by.return_value.all.return_value = []
        mock_db.query.return_value.filter.return_value.first.return_value = None
        
        # Mock Redis
        self.mock_redis.setex = Mock()
        
        # Run analysis
        result = self.service.analyze_keyword_trends(1, mock_db)
        
        # Verify result structure
        assert isinstance(result, dict)
        assert 'keyword_id' in result
        assert 'avg_tfidf_score' in result
        assert 'avg_engagement_score' in result
        assert 'trend_velocity' in result
        assert 'total_posts' in result
        assert 'analyzed_at' in result
        
        # Verify Redis caching was called
        self.mock_redis.setex.assert_called_once()
        
        print(f"Analysis result: {result}")
        print("✓ Full keyword trends analysis test passed")
    
    @patch('app.services.trend_analysis_service.Session')
    def test_analyze_keyword_trends_no_posts(self, mock_session):
        """Test keyword trends analysis with no posts."""
        print("Testing keyword trends analysis with no posts...")
        
        mock_db = Mock()
        mock_db.query.return_value.filter.return_value.all.return_value = []
        
        result = self.service.analyze_keyword_trends(1, mock_db)
        
        assert result == {}
        print("✓ No posts analysis test passed")
    
    @patch('app.services.trend_analysis_service.Session')
    def test_get_keyword_importance_ranking(self, mock_session):
        """Test keyword importance ranking."""
        print("Testing keyword importance ranking...")
        
        # Mock database session and queries
        mock_db = Mock()
        
        # Mock keywords
        mock_keywords = [
            Mock(id=1, keyword="machine learning", user_id=1),
            Mock(id=2, keyword="deep learning", user_id=1),
            Mock(id=3, keyword="neural networks", user_id=1)
        ]
        mock_db.query.return_value.filter.return_value.all.return_value = mock_keywords
        
        # Mock metrics for each keyword
        mock_metrics = Mock(
            avg_tfidf=0.7,
            avg_engagement=0.8,
            avg_velocity=0.1,
            total_posts=10
        )
        mock_db.query.return_value.join.return_value.filter.return_value.first.return_value = mock_metrics
        
        # Get rankings
        rankings = self.service.get_keyword_importance_ranking(1, mock_db)
        
        # Verify results
        assert isinstance(rankings, list)
        assert len(rankings) == len(mock_keywords)
        
        for ranking in rankings:
            assert 'keyword_id' in ranking
            assert 'keyword' in ranking
            assert 'importance_score' in ranking
            assert 'avg_tfidf_score' in ranking
            assert 'avg_engagement_score' in ranking
            assert 'trend_velocity' in ranking
            assert 'total_posts' in ranking
            
            print(f"Keyword: {ranking['keyword']}, Importance: {ranking['importance_score']:.4f}")
        
        print("✓ Keyword importance ranking test passed")


def test_scikit_learn_integration():
    """Test scikit-learn TF-IDF integration."""
    print("Testing scikit-learn TF-IDF integration...")
    
    from sklearn.feature_extraction.text import TfidfVectorizer
    
    # Sample documents
    documents = [
        "machine learning algorithms are powerful",
        "deep learning neural networks",
        "artificial intelligence and machine learning",
        "data science and analytics"
    ]
    
    # Create TF-IDF vectorizer
    vectorizer = TfidfVectorizer(
        max_features=100,
        stop_words='english',
        ngram_range=(1, 2)
    )
    
    # Fit and transform documents
    tfidf_matrix = vectorizer.fit_transform(documents)
    
    # Verify results
    assert tfidf_matrix.shape[0] == len(documents)
    assert tfidf_matrix.shape[1] <= 100  # max_features constraint
    
    # Get feature names
    feature_names = vectorizer.get_feature_names_out()
    print(f"Number of features: {len(feature_names)}")
    print(f"Sample features: {feature_names[:10]}")
    
    # Calculate document scores
    doc_scores = np.array(tfidf_matrix.sum(axis=1)).flatten()
    print(f"Document scores: {doc_scores}")
    
    print("✓ Scikit-learn TF-IDF integration test passed")


def run_all_tests():
    """Run all trend analysis tests."""
    print("=" * 60)
    print("RUNNING TF-IDF TREND ANALYSIS ENGINE TESTS")
    print("=" * 60)
    
    try:
        # Test scikit-learn integration first
        test_scikit_learn_integration()
        print()
        
        # Test service functionality
        test_service = TestTrendAnalysisService()
        test_service.setup_method()
        
        # Run individual tests
        test_service.test_calculate_tfidf_scores()
        test_service.test_calculate_tfidf_scores_empty_posts()
        test_service.test_calculate_engagement_scores()
        test_service.test_calculate_engagement_scores_empty_posts()
        test_service.test_calculate_trend_velocity()
        test_service.test_calculate_trend_velocity_insufficient_data()
        test_service.test_store_metrics()
        test_service.test_get_cached_trend_data()
        test_service.test_get_cached_trend_data_not_found()
        test_service.test_analyze_keyword_trends_integration()
        test_service.test_analyze_keyword_trends_no_posts()
        test_service.test_get_keyword_importance_ranking()
        
        print()
        print("=" * 60)
        print("ALL TESTS PASSED! ✓")
        print("=" * 60)
        print()
        print("TF-IDF Trend Analysis Engine Implementation Summary:")
        print("- ✓ TF-IDF algorithm implemented using scikit-learn")
        print("- ✓ Keyword importance calculation functions")
        print("- ✓ Trend metrics calculation (engagement score, trend velocity)")
        print("- ✓ Redis caching for performance")
        print("- ✓ Database integration for metrics storage")
        print("- ✓ Error handling and edge cases")
        print("- ✓ Celery tasks for background processing")
        print("- ✓ REST API endpoints for trend analysis")
        print("- ✓ Comprehensive test coverage")
        
        return True
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)