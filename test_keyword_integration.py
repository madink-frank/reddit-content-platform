"""
Integration test for keyword management API.
Tests the actual API endpoints with authentication.
"""

import requests
import json
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api/v1"

def test_api_health():
    """Test if the API is running."""
    try:
        response = requests.get(f"{API_BASE}/")
        print(f"API Health Check: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"API Health Check Failed: {e}")
        return False

def test_keyword_endpoints_without_auth():
    """Test keyword endpoints without authentication (should fail)."""
    print("\nTesting keyword endpoints without authentication...")
    
    # Test GET /keywords without auth
    response = requests.get(f"{API_BASE}/keywords/")
    print(f"GET /keywords without auth: {response.status_code}")
    # FastAPI returns 403 when no credentials are provided with HTTPBearer
    assert response.status_code in [401, 403]
    
    # Test POST /keywords without auth
    keyword_data = {"keyword": "test", "is_active": True}
    response = requests.post(f"{API_BASE}/keywords/", json=keyword_data)
    print(f"POST /keywords without auth: {response.status_code}")
    # FastAPI returns 403 when no credentials are provided with HTTPBearer
    assert response.status_code in [401, 403]
    
    print("✅ Authentication protection working correctly")
    return True

def test_openapi_schema():
    """Test that OpenAPI schema includes keyword endpoints."""
    print("\nTesting OpenAPI schema...")
    
    try:
        response = requests.get(f"{API_BASE}/openapi.json")
        if response.status_code == 200:
            schema = response.json()
            paths = schema.get("paths", {})
            
            # Check for keyword endpoints
            keyword_endpoints = [
                "/api/v1/keywords/",
                "/api/v1/keywords/{keyword_id}",
                "/api/v1/keywords/check-duplicate"
            ]
            
            found_endpoints = []
            for endpoint in keyword_endpoints:
                if endpoint in paths:
                    found_endpoints.append(endpoint)
                    print(f"✅ Found endpoint in schema: {endpoint}")
                else:
                    print(f"❌ Missing endpoint in schema: {endpoint}")
            
            if len(found_endpoints) == len(keyword_endpoints):
                print("✅ All keyword endpoints found in OpenAPI schema")
                return True
            else:
                print(f"❌ Only {len(found_endpoints)}/{len(keyword_endpoints)} endpoints found")
                return False
        else:
            print(f"❌ Failed to get OpenAPI schema: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error testing OpenAPI schema: {e}")
        return False

def test_swagger_docs():
    """Test that Swagger docs are accessible."""
    print("\nTesting Swagger documentation...")
    
    try:
        response = requests.get(f"{BASE_URL}/docs")
        if response.status_code == 200:
            print("✅ Swagger docs accessible")
            return True
        else:
            print(f"❌ Swagger docs not accessible: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error accessing Swagger docs: {e}")
        return False

def main():
    """Run all integration tests."""
    print("Starting keyword management integration tests...")
    print("Note: This requires the FastAPI server to be running on localhost:8000")
    print("Start the server with: uvicorn app.main:app --reload")
    
    tests = [
        ("API Health Check", test_api_health),
        ("Authentication Protection", test_keyword_endpoints_without_auth),
        ("OpenAPI Schema", test_openapi_schema),
        ("Swagger Documentation", test_swagger_docs)
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            print(f"\n{'='*50}")
            print(f"Running: {test_name}")
            print('='*50)
            
            if test_func():
                passed += 1
                print(f"✅ {test_name} PASSED")
            else:
                failed += 1
                print(f"❌ {test_name} FAILED")
                
        except Exception as e:
            failed += 1
            print(f"❌ {test_name} FAILED with exception: {e}")
            import traceback
            traceback.print_exc()
    
    print(f"\n{'='*60}")
    print(f"Integration Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All integration tests passed!")
        print("\nNext steps:")
        print("1. Start the server: uvicorn app.main:app --reload")
        print("2. Visit http://localhost:8000/docs to see the API documentation")
        print("3. Test the keyword endpoints with proper authentication")
    else:
        print("❌ Some integration tests failed.")
        print("Make sure the FastAPI server is running on localhost:8000")

if __name__ == "__main__":
    main()