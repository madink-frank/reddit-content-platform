"""
Test authentication endpoints functionality.
"""

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_login_endpoint():
    """Test login endpoint returns redirect."""
    response = client.get("/api/v1/auth/login")
    print(f"Login response status: {response.status_code}")
    print(f"Login response headers: {dict(response.headers)}")
    
    assert response.status_code == 302
    location = response.headers.get("location", "")
    assert "reddit.com" in location
    assert "client_id" in location
    print("✓ Login endpoint working correctly")

def test_protected_endpoints():
    """Test that protected endpoints require authentication."""
    endpoints = [
        "/api/v1/auth/me",
        "/api/v1/auth/status"
    ]
    
    for endpoint in endpoints:
        response = client.get(endpoint)
        print(f"{endpoint} response: {response.status_code}")
        assert response.status_code == 403
        assert "Not authenticated" in response.json()["detail"]
    
    print("✓ Protected endpoints correctly require authentication")

def test_refresh_endpoint():
    """Test refresh token endpoint."""
    response = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": "invalid_token"}
    )
    print(f"Refresh response: {response.status_code}")
    assert response.status_code == 401
    print("✓ Refresh endpoint correctly rejects invalid tokens")

def test_logout_endpoint():
    """Test logout endpoint."""
    response = client.post(
        "/api/v1/auth/logout",
        json={"refresh_token": "invalid_token"}
    )
    print(f"Logout response: {response.status_code}")
    # Should be 403 because no auth header provided
    assert response.status_code == 403
    print("✓ Logout endpoint correctly requires authentication")

def test_openapi_docs():
    """Test that OpenAPI documentation includes auth endpoints."""
    response = client.get("/api/v1/openapi.json")
    assert response.status_code == 200
    
    openapi_spec = response.json()
    paths = openapi_spec.get("paths", {})
    
    auth_endpoints = [
        "/api/v1/auth/login",
        "/api/v1/auth/callback", 
        "/api/v1/auth/refresh",
        "/api/v1/auth/logout",
        "/api/v1/auth/me",
        "/api/v1/auth/status"
    ]
    
    for endpoint in auth_endpoints:
        assert endpoint in paths, f"Endpoint {endpoint} not found in OpenAPI spec"
    
    print("✓ All auth endpoints documented in OpenAPI spec")

def test_health_check():
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
    print("✓ Health check working")

def main():
    """Run all endpoint tests."""
    print("Testing authentication endpoints...\n")
    
    tests = [
        test_login_endpoint,
        test_protected_endpoints,
        test_refresh_endpoint,
        test_logout_endpoint,
        test_openapi_docs,
        test_health_check
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            test()
            passed += 1
            print()
        except Exception as e:
            print(f"❌ Test {test.__name__} failed: {e}")
            import traceback
            traceback.print_exc()
            print()
    
    print(f"📊 Test Results: {passed}/{total} endpoint tests passed")
    
    if passed == total:
        print("🎉 All authentication endpoints are working correctly!")
        return True
    else:
        print("❌ Some authentication endpoints have issues")
        return False

if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)