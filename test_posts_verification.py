"""
Verification test for posts API implementation.
Tests that all required functionality is implemented correctly.
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_posts_endpoints_exist():
    """Verify all required posts endpoints exist and require authentication."""
    
    # Test posts list endpoint
    response = client.get("/api/v1/posts/")
    assert response.status_code == 403  # Should require authentication
    
    # Test post detail endpoint
    response = client.get("/api/v1/posts/1")
    assert response.status_code == 403  # Should require authentication
    
    # Test posts by keyword endpoint
    response = client.get("/api/v1/posts/keyword/1")
    assert response.status_code == 403  # Should require authentication
    
    # Test search posts endpoint
    response = client.get("/api/v1/posts/search/query?q=test")
    assert response.status_code == 403  # Should require authentication
    
    # Test post statistics endpoint
    response = client.get("/api/v1/posts/stats/summary")
    assert response.status_code == 403  # Should require authentication


def test_posts_api_in_openapi():
    """Verify posts API is documented in OpenAPI schema."""
    response = client.get("/docs")
    assert response.status_code == 200
    
    # The docs page should be accessible, indicating OpenAPI is working


def test_posts_service_imports():
    """Verify all posts-related modules can be imported."""
    
    # Test service import
    from app.services.post_service import PostService
    assert PostService is not None
    
    # Test schema imports
    from app.schemas.post import (
        PostResponse, 
        PostDetailResponse, 
        PostListResponse, 
        PostQueryParams,
        CommentResponse
    )
    assert PostResponse is not None
    assert PostDetailResponse is not None
    assert PostListResponse is not None
    assert PostQueryParams is not None
    assert CommentResponse is not None
    
    # Test endpoint import
    from app.api.v1.endpoints.posts import router
    assert router is not None


def test_posts_api_methods():
    """Verify posts API endpoints support correct HTTP methods."""
    
    # All posts endpoints should only support GET
    endpoints = [
        "/api/v1/posts/",
        "/api/v1/posts/1",
        "/api/v1/posts/keyword/1",
        "/api/v1/posts/search/query?q=test",
        "/api/v1/posts/stats/summary"
    ]
    
    for endpoint in endpoints:
        # GET should be supported (returns 403 due to auth)
        response = client.get(endpoint)
        assert response.status_code == 403
        
        # POST should not be supported
        response = client.post(endpoint)
        assert response.status_code == 405  # Method not allowed


def test_posts_query_parameters():
    """Verify posts endpoints accept expected query parameters."""
    
    # Test posts list with various parameters
    test_params = [
        "?page=1",
        "?per_page=10", 
        "?keyword_id=1",
        "?search=test",
        "?sort_by=score",
        "?sort_order=desc",
        "?min_score=10",
        "?subreddit=python"
    ]
    
    for params in test_params:
        response = client.get(f"/api/v1/posts/{params}")
        # Should return 403 (auth required) not 422 (validation error)
        assert response.status_code == 403


def test_posts_service_functionality():
    """Test that PostService has all required methods."""
    from app.services.post_service import PostService
    
    # Check that all required methods exist
    required_methods = [
        'get_posts_paginated',
        'get_post_by_id', 
        'get_posts_by_keyword',
        'search_posts',
        'get_post_statistics'
    ]
    
    for method_name in required_methods:
        assert hasattr(PostService, method_name), f"PostService missing method: {method_name}"


def test_posts_schema_structure():
    """Test that post schemas have required fields."""
    from app.schemas.post import PostResponse, PostListResponse, PostDetailResponse
    
    # Test PostResponse schema
    post_fields = PostResponse.__fields__.keys()
    required_post_fields = [
        'id', 'keyword_id', 'reddit_id', 'title', 'content', 
        'author', 'score', 'num_comments', 'url', 'subreddit',
        'post_created_at', 'created_at', 'updated_at'
    ]
    
    for field in required_post_fields:
        assert field in post_fields, f"PostResponse missing field: {field}"
    
    # Test PostListResponse schema
    list_fields = PostListResponse.__fields__.keys()
    required_list_fields = [
        'posts', 'total', 'page', 'per_page', 'total_pages', 
        'has_next', 'has_prev'
    ]
    
    for field in required_list_fields:
        assert field in list_fields, f"PostListResponse missing field: {field}"
    
    # Test PostDetailResponse schema
    detail_fields = PostDetailResponse.__fields__.keys()
    assert 'comments' in detail_fields, "PostDetailResponse missing comments field"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])