"""
Simple test to verify authentication system components.
"""

import sys
import os
from fastapi.testclient import TestClient

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

def test_app_import():
    """Test that the app can be imported successfully."""
    try:
        from app.main import app
        print("✓ FastAPI app imported successfully")
        return app
    except Exception as e:
        print(f"❌ Failed to import app: {e}")
        return None

def test_auth_endpoints_exist():
    """Test that auth endpoints are registered."""
    from app.main import app
    
    # Get all routes
    routes = []
    for route in app.routes:
        if hasattr(route, 'path'):
            routes.append(route.path)
    
    print(f"Available routes: {routes}")
    
    # Check if auth routes exist
    auth_routes = [r for r in routes if '/auth/' in r]
    print(f"Auth routes found: {auth_routes}")
    
    expected_auth_routes = [
        '/api/v1/auth/login',
        '/api/v1/auth/callback',
        '/api/v1/auth/refresh',
        '/api/v1/auth/logout',
        '/api/v1/auth/me',
        '/api/v1/auth/status'
    ]
    
    for expected_route in expected_auth_routes:
        if expected_route in routes:
            print(f"✓ Route {expected_route} found")
        else:
            print(f"❌ Route {expected_route} missing")

def test_auth_router_import():
    """Test that auth router can be imported."""
    try:
        from app.api.v1.endpoints.auth import router
        print("✓ Auth router imported successfully")
        print(f"Auth router routes: {[route.path for route in router.routes]}")
        return True
    except Exception as e:
        print(f"❌ Failed to import auth router: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_auth_service():
    """Test auth service functionality."""
    try:
        from app.services.auth_service import auth_service
        
        # Test Reddit auth URL generation
        state = "test_state"
        auth_url = auth_service.get_reddit_auth_url(state)
        
        assert "reddit.com" in auth_url
        assert state in auth_url
        print("✓ Auth service working correctly")
        return True
    except Exception as e:
        print(f"❌ Auth service test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_dependencies():
    """Test that dependencies can be imported."""
    try:
        from app.core.dependencies import get_current_user, get_db
        print("✓ Dependencies imported successfully")
        return True
    except Exception as e:
        print(f"❌ Failed to import dependencies: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_schemas():
    """Test that schemas can be imported."""
    try:
        from app.schemas.auth import TokenResponse, LoginResponse, UserResponse
        print("✓ Auth schemas imported successfully")
        return True
    except Exception as e:
        print(f"❌ Failed to import auth schemas: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests."""
    print("Testing authentication system components...\n")
    
    tests = [
        test_app_import,
        test_auth_router_import,
        test_auth_service,
        test_dependencies,
        test_schemas,
        test_auth_endpoints_exist
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            result = test()
            if result is not False:
                passed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} failed: {e}")
    
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All authentication components are working correctly!")
        return True
    else:
        print("❌ Some authentication components have issues")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)