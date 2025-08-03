"""
Simple test for keyword management functionality.
Tests the service layer directly without full database setup.
"""

import asyncio
from unittest.mock import Mock, AsyncMock
from sqlalchemy.orm import Session

from app.services.keyword_service import KeywordService
from app.schemas.keyword import KeywordCreate, KeywordUpdate
from app.models.keyword import Keyword
from app.models.user import User

def test_keyword_service():
    """Test keyword service functionality with mocked database."""
    print("Testing keyword service...")
    
    # Mock database session
    mock_db = Mock(spec=Session)
    
    # Create service instance
    service = KeywordService(mock_db)
    
    # Test data
    user_id = 1
    keyword_data = KeywordCreate(keyword="python programming", is_active=True)
    
    # Mock existing keyword query (no duplicates)
    mock_db.query.return_value.filter.return_value.first.return_value = None
    
    # Mock keyword creation
    mock_keyword = Keyword(
        id=1,
        user_id=user_id,
        keyword="python programming",
        is_active=True
    )
    
    mock_db.add = Mock()
    mock_db.commit = Mock()
    mock_db.refresh = Mock()
    
    print("✅ Keyword service setup completed")
    
    # Test schema validation
    print("Testing schema validation...")
    
    # Valid keyword
    valid_keyword = KeywordCreate(keyword="  Machine Learning  ", is_active=True)
    assert valid_keyword.keyword == "machine learning"  # Should be normalized
    
    # Test update schema
    update_data = KeywordUpdate(keyword="  Deep Learning  ")
    assert update_data.keyword == "deep learning"
    
    print("✅ Schema validation passed")

def test_keyword_validation():
    """Test keyword validation logic."""
    print("Testing keyword validation...")
    
    # Test valid keywords
    valid_keywords = [
        "python",
        "machine learning",
        "artificial intelligence",
        "data science",
        "web development"
    ]
    
    for keyword in valid_keywords:
        try:
            schema = KeywordCreate(keyword=keyword, is_active=True)
            print(f"✅ Valid keyword: '{keyword}' -> '{schema.keyword}'")
        except Exception as e:
            print(f"❌ Unexpected error for '{keyword}': {e}")
            return False
    
    # Test invalid keywords
    invalid_keywords = [
        "",
        "   ",
        "\t\n"
    ]
    
    for keyword in invalid_keywords:
        try:
            schema = KeywordCreate(keyword=keyword, is_active=True)
            print(f"❌ Should have failed for: '{keyword}'")
            return False
        except ValueError:
            print(f"✅ Correctly rejected invalid keyword: '{keyword}'")
        except Exception as e:
            print(f"❌ Unexpected error type for '{keyword}': {e}")
            return False
    
    print("✅ Keyword validation passed")
    return True

def test_api_endpoints_structure():
    """Test that API endpoints are properly structured."""
    print("Testing API endpoint structure...")
    
    from app.api.v1.endpoints.keywords import router
    
    # Check that router exists and has routes
    assert router is not None
    assert len(router.routes) > 0
    
    # Check route paths
    route_paths = [route.path for route in router.routes]
    expected_paths = ["/", "/{keyword_id}", "/check-duplicate"]
    
    for path in expected_paths:
        if path in route_paths:
            print(f"✅ Found expected route: {path}")
        else:
            print(f"❌ Missing expected route: {path}")
            return False
    
    print("✅ API endpoint structure passed")
    return True

def test_schema_serialization():
    """Test that schemas can be properly serialized."""
    print("Testing schema serialization...")
    
    from app.schemas.keyword import KeywordResponse, KeywordListResponse
    from datetime import datetime
    
    # Test KeywordResponse
    keyword_data = {
        "id": 1,
        "user_id": 1,
        "keyword": "python",
        "is_active": True,
        "created_at": datetime.now(),
        "updated_at": datetime.now()
    }
    
    try:
        response = KeywordResponse(**keyword_data)
        print(f"✅ KeywordResponse serialization: {response.keyword}")
    except Exception as e:
        print(f"❌ KeywordResponse serialization failed: {e}")
        return False
    
    # Test KeywordListResponse
    list_data = {
        "keywords": [response],
        "total": 1,
        "page": 1,
        "per_page": 20,
        "total_pages": 1
    }
    
    try:
        list_response = KeywordListResponse(**list_data)
        print(f"✅ KeywordListResponse serialization: {list_response.total} keywords")
    except Exception as e:
        print(f"❌ KeywordListResponse serialization failed: {e}")
        return False
    
    print("✅ Schema serialization passed")
    return True

def test_import_structure():
    """Test that all imports work correctly."""
    print("Testing import structure...")
    
    try:
        from app.schemas.keyword import (
            KeywordCreate, 
            KeywordUpdate, 
            KeywordResponse, 
            KeywordListResponse
        )
        print("✅ Keyword schemas imported successfully")
        
        from app.services.keyword_service import KeywordService
        print("✅ Keyword service imported successfully")
        
        from app.api.v1.endpoints.keywords import router
        print("✅ Keyword router imported successfully")
        
        from app.models.keyword import Keyword
        print("✅ Keyword model imported successfully")
        
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False
    
    print("✅ Import structure passed")
    return True

if __name__ == "__main__":
    print("Starting keyword management tests...\n")
    
    tests = [
        test_import_structure,
        test_keyword_validation,
        test_schema_serialization,
        test_api_endpoints_structure,
        test_keyword_service
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            print(f"\n--- Running {test.__name__} ---")
            if test():
                passed += 1
                print(f"✅ {test.__name__} PASSED")
            else:
                failed += 1
                print(f"❌ {test.__name__} FAILED")
        except Exception as e:
            failed += 1
            print(f"❌ {test.__name__} FAILED with exception: {e}")
            import traceback
            traceback.print_exc()
    
    print(f"\n{'='*50}")
    print(f"Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All tests passed successfully!")
    else:
        print("❌ Some tests failed. Please check the implementation.")