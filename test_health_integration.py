"""
Integration test for health check endpoints.
"""

import pytest
import asyncio
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


class TestHealthIntegration:
    """Integration tests for health check endpoints."""
    
    def test_liveness_endpoint(self, client):
        """Test liveness endpoint - should always work."""
        response = client.get("/api/v1/health/live")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "alive"
        assert data["service"] == "reddit-content-platform"
    
    def test_health_endpoint_basic(self, client):
        """Test basic health endpoint."""
        response = client.get("/api/v1/health/")
        
        # Should return either 200 (healthy) or 503 (unhealthy)
        assert response.status_code in [200, 503]
        
        data = response.json()
        if response.status_code == 200:
            assert "status" in data
            assert "timestamp" in data
            assert data["status"] == "healthy"
        else:
            # When unhealthy, FastAPI returns error detail
            assert "detail" in data
    
    def test_health_endpoint_with_details(self, client):
        """Test health endpoint with details."""
        response = client.get("/api/v1/health/?details=true")
        
        # Should return either 200 (healthy) or 503 (unhealthy)
        assert response.status_code in [200, 503]
        
        data = response.json()
        
        # If healthy, should have services details
        if response.status_code == 200:
            assert "status" in data
            assert "timestamp" in data
            assert "services" in data
            assert "database" in data["services"]
            assert "redis" in data["services"]
            assert "celery" in data["services"]
            assert "reddit_api" in data["services"]
        else:
            # When unhealthy, FastAPI returns error detail
            assert "detail" in data
    
    def test_readiness_endpoint(self, client):
        """Test readiness endpoint."""
        response = client.get("/api/v1/health/ready")
        
        # Should return either 200 (ready) or 503 (not ready)
        assert response.status_code in [200, 503]
        
        data = response.json()
        if response.status_code == 200:
            assert data["status"] == "ready"
            assert "timestamp" in data
    
    def test_individual_service_endpoints(self, client):
        """Test individual service health endpoints."""
        services = ["database", "redis", "celery", "reddit"]
        
        for service in services:
            response = client.get(f"/api/v1/health/{service}")
            
            # Should return 200 (healthy), 503 (unhealthy), or 500 (error)
            assert response.status_code in [200, 503, 500]
            
            if response.status_code == 200:
                data = response.json()
                assert "service" in data
                assert "status" in data
                assert "response_time_ms" in data
                assert data["status"] == "healthy"
    
    def test_health_endpoints_in_openapi_docs(self, client):
        """Test that health endpoints are documented in OpenAPI."""
        # Try different possible OpenAPI endpoints
        openapi_urls = ["/openapi.json", "/docs/openapi.json", "/api/v1/openapi.json"]
        
        openapi_spec = None
        for url in openapi_urls:
            response = client.get(url)
            if response.status_code == 200:
                openapi_spec = response.json()
                break
        
        # If we can't find OpenAPI spec, skip this test
        if openapi_spec is None:
            pytest.skip("OpenAPI specification not accessible")
        
        # Check that health endpoints are documented
        paths = openapi_spec.get("paths", {})
        
        health_endpoints = [
            "/api/v1/health/",
            "/api/v1/health/database",
            "/api/v1/health/redis", 
            "/api/v1/health/celery",
            "/api/v1/health/reddit",
            "/api/v1/health/ready",
            "/api/v1/health/live"
        ]
        
        for endpoint in health_endpoints:
            assert endpoint in paths, f"Health endpoint {endpoint} not found in OpenAPI spec"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])