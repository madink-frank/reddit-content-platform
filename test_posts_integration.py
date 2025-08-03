"""
Integration test for posts API - tests the actual functionality without database conflicts.
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_posts_api_structure():
    """Test that posts API endpoints are properly registered."""
    # Test that the API is accessible
    response = client.get("/api/v1/")
    assert response.status_code == 200
    
    # Test that posts endpoints exist (should return 401/403 for unauthorized access)
    response = client.get("/api/v1/posts/")
    assert response.status_code in [401, 403]  # Should require authentication
    
    response = client.get("/api/v1/posts/1")
    assert response.status_code in [401, 403]  # Should require authentication
    
    response = client.get("/api/v1/posts/keyword/1")
    assert response.status_code in [401, 403]  # Should require authentication
    
    response = client.get("/api/v1/posts/search/query?q=test")
    assert response.status_code in [401, 403]  # Should require authentication
    
    response = client.get("/api/v1/posts/stats/summary")
    assert response.status_code in [401, 403]  # Should require authentication


def test_posts_api_documentation():
    """Test that posts API is documented in OpenAPI."""
    response = client.get("/openapi.json")
    assert response.status_code == 200
    
    openapi_spec = response.json()
    
    # Check that posts endpoints are documented
    paths = openapi_spec.get("paths", {})
    
    assert "/api/v1/posts/" in paths
    assert "/api/v1/posts/{post_id}" in paths
    assert "/api/v1/posts/keyword/{keyword_id}" in paths
    assert "/api/v1/posts/search/query" in paths
    assert "/api/v1/posts/stats/summary" in paths
    
    # Check that the posts endpoints have proper HTTP methods
    posts_endpoint = paths.get("/api/v1/posts/", {})
    assert "get" in posts_endpoint
    
    post_detail_endpoint = paths.get("/api/v1/posts/{post_id}", {})
    assert "get" in post_detail_endpoint


def test_posts_api_parameters():
    """Test that posts API endpoints have proper parameters documented."""
    response = client.get("/openapi.json")
    openapi_spec = response.json()
    paths = openapi_spec.get("paths", {})
    
    # Check posts list endpoint parameters
    posts_get = paths.get("/api/v1/posts/", {}).get("get", {})
    parameters = posts_get.get("parameters", [])
    
    # Should have pagination and filtering parameters
    param_names = [p.get("name") for p in parameters]
    
    assert "page" in param_names
    assert "per_page" in param_names
    assert "keyword_id" in param_names
    assert "search" in param_names
    assert "sort_by" in param_names
    assert "sort_order" in param_names


if __name__ == "__main__":
    pytest.main([__file__, "-v"])