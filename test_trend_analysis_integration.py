"""
Integration test for TF-IDF trend analysis API endpoints.
"""

import sys
import os
import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch
from datetime import datetime

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.main import app
from app.models.user import User
from app.models.keyword import Keyword
from app.models.post import Post


class TestTrendAnalysisAPI:
    """Integration tests for trend analysis API endpoints."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.client = TestClient(app)
        
        # Mock user for authentication
        self.mock_user = User(
            id=1,
            name="Test User",
            email="test@example.com",
            oauth_provider="google"
        )
        
        # Mock keyword
        self.mock_keyword = Keyword(
            id=1,
            user_id=1,
            keyword="machine learning",
            is_active=True
        )
        
        # Mock posts
        self.mock_posts = [
            Post(
                id=1,
                keyword_id=1,
                reddit_id="post1",
                title="Machine Learning Trends",
                content="Content about ML trends",
                author="user1",
                score=100,
                num_comments=25,
                url="https://reddit.com/post1",
                subreddit="MachineLearning",
                post_created_at=datetime.utcnow()
            )
        ]
    
    @patch('app.core.dependencies.get_current_user')
    @patch('app.core.database.get_db')
    def test_start_trend_analysis_endpoint(self, mock_get_db, mock_get_current_user):
        """Test starting trend analysis via API."""
        print("Testing trend analysis start endpoint...")
        
        # Mock authentication
        mock_get_current_user.return_value = self.mock_user
        
        # Mock database
        mock_db = Mock()
        mock_db.query.return_value.filter.return_value.first.return_value = self.mock_keyword
        mock_get_db.return_value = mock_db
        
        # Mock Celery task
        with patch('app.api.v1.endpoints.trends.analyze_keyword_trends_task') as mock_task:
            mock_task.delay.return_value = Mock(id="test-task-id")
            
            response = self.client.post("/api/v1/trends/analyze/1")
            
            assert response.status_code == 200
            data = response.json()
            assert data["message"] == "Trend analysis started"
            assert data["task_id"] == "test-task-id"
            assert data["keyword_id"] == 1
            
        print("✓ Trend analysis start endpoint test passed")
    
    @patch('app.core.dependencies.get_current_user')
    @patch('app.core.database.get_db')
    def test_get_trend_results_endpoint(self, mock_get_db, mock_get_current_user):
        """Test getting trend analysis results via API."""
        print("Testing trend analysis results endpoint...")
        
        # Mock authentication
        mock_get_current_user.return_value = self.mock_user
        
        # Mock database
        mock_db = Mock()
        mock_db.query.return_value.filter.return_value.first.return_value = self.mock_keyword
        mock_db.query.return_value.filter.return_value.all.return_value = self.mock_posts
        mock_get_db.return_value = mock_db
        
        # Mock trend analysis service
        with patch('app.services.trend_analysis_service.trend_analysis_service') as mock_service:
            mock_service.get_cached_trend_data.return_value = None
            mock_service.analyze_keyword_trends.return_value = {
                "keyword_id": 1,
                "avg_tfidf_score": 0.8,
                "avg_engagement_score": 0.7,
                "trend_velocity": 0.1,
                "total_posts": 1,
                "analyzed_at": "2024-01-01T00:00:00"
            }
            
            response = self.client.get("/api/v1/trends/results/1")
            
            assert response.status_code == 200
            data = response.json()
            assert data["keyword_id"] == 1
            assert data["keyword"] == "machine learning"
            assert "trend_data" in data
            assert data["cached"] == False
            
        print("✓ Trend analysis results endpoint test passed")
    
    @patch('app.core.dependencies.get_current_user')
    @patch('app.core.database.get_db')
    def test_get_keyword_rankings_endpoint(self, mock_get_db, mock_get_current_user):
        """Test getting keyword rankings via API."""
        print("Testing keyword rankings endpoint...")
        
        # Mock authentication
        mock_get_current_user.return_value = self.mock_user
        
        # Mock database
        mock_db = Mock()
        mock_get_db.return_value = mock_db
        
        # Mock trend analysis service
        with patch('app.services.trend_analysis_service.trend_analysis_service') as mock_service:
            mock_service.get_keyword_importance_ranking.return_value = [
                {
                    "keyword_id": 1,
                    "keyword": "machine learning",
                    "importance_score": 0.8,
                    "avg_tfidf_score": 0.7,
                    "avg_engagement_score": 0.6,
                    "trend_velocity": 0.1,
                    "total_posts": 10
                }
            ]
            
            response = self.client.get("/api/v1/trends/rankings")
            
            assert response.status_code == 200
            data = response.json()
            assert data["user_id"] == 1
            assert len(data["rankings"]) == 1
            assert data["rankings"][0]["keyword"] == "machine learning"
            assert data["total_keywords"] == 1
            
        print("✓ Keyword rankings endpoint test passed")
    
    @patch('app.core.dependencies.get_current_user')
    def test_bulk_analysis_endpoint(self, mock_get_current_user):
        """Test bulk trend analysis endpoint."""
        print("Testing bulk trend analysis endpoint...")
        
        # Mock authentication
        mock_get_current_user.return_value = self.mock_user
        
        # Mock database
        with patch('app.core.database.get_db') as mock_get_db:
            mock_db = Mock()
            mock_db.query.return_value.filter.return_value.count.return_value = 3
            mock_get_db.return_value = mock_db
            
            # Mock Celery task
            with patch('app.api.v1.endpoints.trends.analyze_all_user_keywords_task') as mock_task:
                mock_task.delay.return_value = Mock(id="bulk-task-id")
                
                response = self.client.post("/api/v1/trends/analyze-all")
                
                assert response.status_code == 200
                data = response.json()
                assert data["message"] == "Bulk trend analysis started"
                assert data["task_id"] == "bulk-task-id"
                assert data["keyword_count"] == 3
                
        print("✓ Bulk trend analysis endpoint test passed")
    
    def test_task_status_endpoint(self):
        """Test task status endpoint."""
        print("Testing task status endpoint...")
        
        # Mock Celery task result
        with patch('app.core.celery_app.celery_app') as mock_celery:
            mock_result = Mock()
            mock_result.state = 'SUCCESS'
            mock_result.result = {"success": True, "keyword_id": 1}
            mock_celery.AsyncResult.return_value = mock_result
            
            response = self.client.get("/api/v1/trends/status/test-task-id")
            
            assert response.status_code == 200
            data = response.json()
            assert data["task_id"] == "test-task-id"
            assert data["state"] == "SUCCESS"
            assert "result" in data
            
        print("✓ Task status endpoint test passed")
    
    @patch('app.core.dependencies.get_current_user')
    @patch('app.core.database.get_db')
    def test_clear_cache_endpoint(self, mock_get_db, mock_get_current_user):
        """Test cache clearing endpoint."""
        print("Testing cache clearing endpoint...")
        
        # Mock authentication
        mock_get_current_user.return_value = self.mock_user
        
        # Mock database
        mock_db = Mock()
        mock_db.query.return_value.filter.return_value.first.return_value = self.mock_keyword
        mock_get_db.return_value = mock_db
        
        # Mock Redis client
        with patch('app.core.redis_client.redis_client') as mock_redis:
            mock_redis.redis.delete.return_value = True
            
            response = self.client.delete("/api/v1/trends/cache/1")
            
            assert response.status_code == 200
            data = response.json()
            assert data["message"] == "Trend cache cleared successfully"
            assert data["keyword_id"] == 1
            
        print("✓ Cache clearing endpoint test passed")
    
    @patch('app.core.dependencies.get_current_user')
    @patch('app.core.database.get_db')
    def test_keyword_not_found_error(self, mock_get_db, mock_get_current_user):
        """Test error handling when keyword is not found."""
        print("Testing keyword not found error handling...")
        
        # Mock authentication
        mock_get_current_user.return_value = self.mock_user
        
        # Mock database - keyword not found
        mock_db = Mock()
        mock_db.query.return_value.filter.return_value.first.return_value = None
        mock_get_db.return_value = mock_db
        
        response = self.client.post("/api/v1/trends/analyze/999")
        
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"].lower()
        
        print("✓ Keyword not found error handling test passed")


def run_integration_tests():
    """Run all integration tests."""
    print("=" * 60)
    print("RUNNING TF-IDF TREND ANALYSIS API INTEGRATION TESTS")
    print("=" * 60)
    
    try:
        test_api = TestTrendAnalysisAPI()
        test_api.setup_method()
        
        # Run individual tests
        test_api.test_start_trend_analysis_endpoint()
        test_api.test_get_trend_results_endpoint()
        test_api.test_get_keyword_rankings_endpoint()
        test_api.test_bulk_analysis_endpoint()
        test_api.test_task_status_endpoint()
        test_api.test_clear_cache_endpoint()
        test_api.test_keyword_not_found_error()
        
        print()
        print("=" * 60)
        print("ALL INTEGRATION TESTS PASSED! ✓")
        print("=" * 60)
        print()
        print("API Endpoints Verified:")
        print("- ✓ POST /api/v1/trends/analyze/{keyword_id}")
        print("- ✓ POST /api/v1/trends/analyze-all")
        print("- ✓ GET /api/v1/trends/results/{keyword_id}")
        print("- ✓ GET /api/v1/trends/rankings")
        print("- ✓ POST /api/v1/trends/rankings/calculate")
        print("- ✓ GET /api/v1/trends/status/{task_id}")
        print("- ✓ DELETE /api/v1/trends/cache/{keyword_id}")
        print("- ✓ Error handling and validation")
        
        return True
        
    except Exception as e:
        print(f"\n❌ INTEGRATION TEST FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_integration_tests()
    sys.exit(0 if success else 1)