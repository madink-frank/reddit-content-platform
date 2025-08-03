"""
Test health check endpoints implementation.
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from fastapi.testclient import TestClient
from app.main import app
from app.services.health_check_service import health_service


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


@pytest.fixture
def mock_health_service():
    """Mock health service for testing."""
    return AsyncMock()


class TestHealthEndpoints:
    """Test health check endpoints."""
    
    def test_health_check_healthy(self, client):
        """Test health check endpoint when all services are healthy."""
        with patch.object(health_service, 'get_health_status') as mock_health:
            mock_health.return_value = {
                "status": "healthy",
                "timestamp": "2024-01-01T00:00:00Z"
            }
            
            response = client.get("/api/v1/health/")
            
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "healthy"
            assert "timestamp" in data
    
    def test_health_check_unhealthy(self, client):
        """Test health check endpoint when services are unhealthy."""
        with patch.object(health_service, 'get_health_status') as mock_health:
            mock_health.return_value = {
                "status": "unhealthy",
                "timestamp": "2024-01-01T00:00:00Z"
            }
            
            response = client.get("/api/v1/health/")
            
            assert response.status_code == 503
    
    def test_health_check_with_details(self, client):
        """Test health check endpoint with detailed service information."""
        with patch.object(health_service, 'get_health_status') as mock_health:
            mock_health.return_value = {
                "status": "healthy",
                "timestamp": "2024-01-01T00:00:00Z",
                "services": {
                    "database": {"status": "healthy", "response_time_ms": 10.5},
                    "redis": {"status": "healthy", "response_time_ms": 5.2},
                    "celery": {"status": "healthy", "response_time_ms": 15.8},
                    "reddit_api": {"status": "healthy", "response_time_ms": 120.3}
                }
            }
            
            response = client.get("/api/v1/health/?details=true")
            
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "healthy"
            assert "services" in data
            assert len(data["services"]) == 4
    
    def test_database_health_check(self, client):
        """Test database health check endpoint."""
        with patch.object(health_service, 'get_service_health') as mock_health:
            mock_health.return_value = {
                "service": "database",
                "status": "healthy",
                "response_time_ms": 10.5,
                "details": {"connection_pool": "active"}
            }
            
            response = client.get("/api/v1/health/database")
            
            assert response.status_code == 200
            data = response.json()
            assert data["service"] == "database"
            assert data["status"] == "healthy"
            assert data["response_time_ms"] == 10.5
    
    def test_redis_health_check(self, client):
        """Test Redis health check endpoint."""
        with patch.object(health_service, 'get_service_health') as mock_health:
            mock_health.return_value = {
                "service": "redis",
                "status": "healthy",
                "response_time_ms": 5.2,
                "details": {"connection": "active"}
            }
            
            response = client.get("/api/v1/health/redis")
            
            assert response.status_code == 200
            data = response.json()
            assert data["service"] == "redis"
            assert data["status"] == "healthy"
            assert data["response_time_ms"] == 5.2
    
    def test_celery_health_check(self, client):
        """Test Celery health check endpoint."""
        with patch.object(health_service, 'get_service_health') as mock_health:
            mock_health.return_value = {
                "service": "celery",
                "status": "healthy",
                "response_time_ms": 15.8,
                "active_workers": 2,
                "details": {"workers": ["worker1", "worker2"]}
            }
            
            response = client.get("/api/v1/health/celery")
            
            assert response.status_code == 200
            data = response.json()
            assert data["service"] == "celery"
            assert data["status"] == "healthy"
            assert data["response_time_ms"] == 15.8
    
    def test_reddit_api_health_check(self, client):
        """Test Reddit API health check endpoint."""
        with patch.object(health_service, 'get_service_health') as mock_health:
            mock_health.return_value = {
                "service": "reddit_api",
                "status": "healthy",
                "response_time_ms": 120.3,
                "details": {
                    "message": "Reddit API connection is working",
                    "timestamp": "2024-01-01T00:00:00Z"
                }
            }
            
            response = client.get("/api/v1/health/reddit")
            
            assert response.status_code == 200
            data = response.json()
            assert data["service"] == "reddit_api"
            assert data["status"] == "healthy"
            assert data["response_time_ms"] == 120.3
    
    def test_service_health_unhealthy(self, client):
        """Test service health check when service is unhealthy."""
        with patch.object(health_service, 'get_service_health') as mock_health:
            mock_health.return_value = {
                "service": "database",
                "status": "unhealthy",
                "response_time_ms": 5000.0,
                "error": "Connection timeout"
            }
            
            response = client.get("/api/v1/health/database")
            
            assert response.status_code == 503
    
    def test_service_not_found(self, client):
        """Test service health check for non-existent service."""
        with patch.object(health_service, 'get_service_health') as mock_health:
            mock_health.return_value = {
                "error": "service_not_found",
                "detail": "Service 'invalid' not found"
            }
            
            response = client.get("/api/v1/health/database")
            
            assert response.status_code == 404
    
    def test_readiness_check_ready(self, client):
        """Test readiness probe when service is ready."""
        with patch.object(health_service, 'get_health_status') as mock_health:
            mock_health.return_value = {
                "status": "healthy",
                "timestamp": "2024-01-01T00:00:00Z"
            }
            
            response = client.get("/api/v1/health/ready")
            
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "ready"
            assert "timestamp" in data
    
    def test_readiness_check_not_ready(self, client):
        """Test readiness probe when service is not ready."""
        with patch.object(health_service, 'get_health_status') as mock_health:
            mock_health.return_value = {
                "status": "unhealthy",
                "timestamp": "2024-01-01T00:00:00Z"
            }
            
            response = client.get("/api/v1/health/ready")
            
            assert response.status_code == 503
    
    def test_liveness_check(self, client):
        """Test liveness probe."""
        response = client.get("/api/v1/health/live")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "alive"
        assert data["service"] == "reddit-content-platform"
    
    def test_health_check_exception_handling(self, client):
        """Test health check exception handling."""
        with patch.object(health_service, 'get_health_status') as mock_health:
            mock_health.side_effect = Exception("Unexpected error")
            
            response = client.get("/api/v1/health/")
            
            assert response.status_code == 500


class TestHealthService:
    """Test health check service directly."""
    
    @pytest.mark.asyncio
    async def test_database_health_check_success(self):
        """Test database health check success."""
        with patch('app.services.health_check_service.SessionLocal') as mock_session_local:
            mock_db = MagicMock()
            mock_session_local.return_value = mock_db
            mock_db.execute.return_value = None
            
            result = await health_service._check_database()
            
            assert result["status"] == "healthy"
            assert "response_time_ms" in result
            assert result["details"]["connection_pool"] == "active"
    
    @pytest.mark.asyncio
    async def test_database_health_check_failure(self):
        """Test database health check failure."""
        with patch('app.services.health_check_service.SessionLocal') as mock_session_local:
            mock_db = MagicMock()
            mock_session_local.return_value = mock_db
            mock_db.execute.side_effect = Exception("Connection failed")
            
            result = await health_service._check_database()
            
            assert result["status"] == "unhealthy"
            assert "error" in result
            assert "response_time_ms" in result
    
    @pytest.mark.asyncio
    async def test_redis_health_check_success(self):
        """Test Redis health check success."""
        with patch('app.services.health_check_service.redis_client') as mock_redis:
            mock_redis.ping.return_value = True
            
            result = await health_service._check_redis()
            
            assert result["status"] == "healthy"
            assert "response_time_ms" in result
            assert result["details"]["connection"] == "active"
    
    @pytest.mark.asyncio
    async def test_redis_health_check_failure(self):
        """Test Redis health check failure."""
        with patch('app.services.health_check_service.redis_client') as mock_redis:
            mock_redis.ping.side_effect = Exception("Redis connection failed")
            
            result = await health_service._check_redis()
            
            assert result["status"] == "unhealthy"
            assert "error" in result
            assert "response_time_ms" in result
    
    @pytest.mark.asyncio
    async def test_celery_health_check_success(self):
        """Test Celery health check success."""
        with patch('app.services.health_check_service.celery_app') as mock_celery:
            mock_inspect = MagicMock()
            mock_celery.control.inspect.return_value = mock_inspect
            mock_inspect.active.return_value = {
                "worker1": [],
                "worker2": []
            }
            
            result = await health_service._check_celery()
            
            assert result["status"] == "healthy"
            assert result["active_workers"] == 2
            assert "response_time_ms" in result
    
    @pytest.mark.asyncio
    async def test_celery_health_check_no_workers(self):
        """Test Celery health check with no active workers."""
        with patch('app.services.health_check_service.celery_app') as mock_celery:
            mock_inspect = MagicMock()
            mock_celery.control.inspect.return_value = mock_inspect
            mock_inspect.active.return_value = {}
            
            result = await health_service._check_celery()
            
            assert result["status"] == "unhealthy"
            assert result["active_workers"] == 0
            assert "error" in result
    
    @pytest.mark.asyncio
    async def test_reddit_api_health_check_success(self):
        """Test Reddit API health check success."""
        with patch('app.services.health_check_service.reddit_client') as mock_reddit:
            # Make it an async mock
            mock_reddit.health_check = AsyncMock(return_value={
                "status": "healthy",
                "message": "Reddit API connection is working",
                "timestamp": "2024-01-01T00:00:00Z"
            })
            
            result = await health_service._check_reddit_api()
            
            assert result["status"] == "healthy"
            assert "response_time_ms" in result
            assert result["details"]["message"] == "Reddit API connection is working"
    
    @pytest.mark.asyncio
    async def test_reddit_api_health_check_failure(self):
        """Test Reddit API health check failure."""
        with patch('app.services.health_check_service.reddit_client') as mock_reddit:
            mock_reddit.health_check.side_effect = Exception("Reddit API error")
            
            result = await health_service._check_reddit_api()
            
            assert result["status"] == "unhealthy"
            assert "error" in result
            assert "response_time_ms" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])