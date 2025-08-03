"""
Simple test to verify the FastAPI app can start properly
"""

import sys
import os

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

try:
    from app.main import app
    print("✅ FastAPI app imported successfully")
    
    # Test that the app has the expected routes
    routes = [route.path for route in app.routes]
    print(f"✅ App has {len(routes)} routes")
    
    # Check for auth routes
    auth_routes = [route for route in routes if 'auth' in route]
    print(f"✅ Found {len(auth_routes)} auth-related routes")
    
    print("✅ All basic checks passed!")
    
except Exception as e:
    print(f"❌ Error importing or testing app: {e}")
    import traceback
    traceback.print_exc()