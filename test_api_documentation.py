#!/usr/bin/env python3
"""
Test script to verify API documentation is working correctly.
"""

import json
import requests
import subprocess
import time
import sys
from pathlib import Path


def test_openapi_schema():
    """Test that OpenAPI schema is valid and accessible."""
    print("🔧 Testing OpenAPI schema...")
    
    # Check if schema file exists
    schema_file = Path("docs/api/openapi.json")
    if not schema_file.exists():
        print("❌ OpenAPI schema file not found")
        return False
    
    # Load and validate JSON
    try:
        with open(schema_file, "r") as f:
            schema = json.load(f)
        
        # Check required fields
        required_fields = ["openapi", "info", "paths"]
        for field in required_fields:
            if field not in schema:
                print(f"❌ Missing required field: {field}")
                return False
        
        # Check version
        if schema["info"]["version"] != "1.0.0":
            print(f"❌ Unexpected version: {schema['info']['version']}")
            return False
        
        print("✅ OpenAPI schema is valid")
        return True
        
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON in OpenAPI schema: {e}")
        return False
    except Exception as e:
        print(f"❌ Error reading OpenAPI schema: {e}")
        return False


def test_postman_collection():
    """Test that Postman collection is valid."""
    print("🔧 Testing Postman collection...")
    
    collection_file = Path("postman/Reddit_Content_Platform_API.postman_collection.json")
    env_file = Path("postman/Reddit_Content_Platform_Environment.postman_environment.json")
    
    # Check if files exist
    if not collection_file.exists():
        print("❌ Postman collection file not found")
        return False
    
    if not env_file.exists():
        print("❌ Postman environment file not found")
        return False
    
    try:
        # Load and validate collection
        with open(collection_file, "r") as f:
            collection = json.load(f)
        
        # Check required fields
        if "info" not in collection or "item" not in collection:
            print("❌ Invalid Postman collection structure")
            return False
        
        # Check version
        if collection["info"]["version"] != "1.0.0":
            print(f"❌ Unexpected collection version: {collection['info']['version']}")
            return False
        
        # Load and validate environment
        with open(env_file, "r") as f:
            environment = json.load(f)
        
        # Check required environment variables
        required_vars = ["base_url", "access_token", "refresh_token"]
        env_vars = {var["key"] for var in environment["values"]}
        
        for var in required_vars:
            if var not in env_vars:
                print(f"❌ Missing environment variable: {var}")
                return False
        
        print("✅ Postman collection and environment are valid")
        return True
        
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON in Postman files: {e}")
        return False
    except Exception as e:
        print(f"❌ Error reading Postman files: {e}")
        return False


def test_code_examples():
    """Test that code examples exist and are syntactically valid."""
    print("🔧 Testing code examples...")
    
    examples_dir = Path("docs/api/examples")
    if not examples_dir.exists():
        print("❌ Examples directory not found")
        return False
    
    # Check Python example
    python_file = examples_dir / "python_examples.py"
    if not python_file.exists():
        print("❌ Python examples file not found")
        return False
    
    try:
        # Try to compile Python code
        with open(python_file, "r") as f:
            python_code = f.read()
        compile(python_code, python_file, "exec")
        print("✅ Python examples are syntactically valid")
    except SyntaxError as e:
        print(f"❌ Python syntax error: {e}")
        return False
    
    # Check JavaScript example
    js_file = examples_dir / "javascript_examples.js"
    if not js_file.exists():
        print("❌ JavaScript examples file not found")
        return False
    
    # Check cURL example
    curl_file = examples_dir / "curl_examples.sh"
    if not curl_file.exists():
        print("❌ cURL examples file not found")
        return False
    
    # Check if cURL script is executable
    if not curl_file.stat().st_mode & 0o111:
        print("❌ cURL examples script is not executable")
        return False
    
    print("✅ All code examples exist and are valid")
    return True


def test_api_server():
    """Test that API server serves documentation correctly."""
    print("🔧 Testing API server documentation endpoints...")
    
    # Start server in background
    try:
        import uvicorn
        from app.main import app
        import threading
        import time
        
        # Start server in a separate thread
        def run_server():
            uvicorn.run(app, host="127.0.0.1", port=8001, log_level="error")
        
        server_thread = threading.Thread(target=run_server, daemon=True)
        server_thread.start()
        
        # Wait for server to start
        time.sleep(3)
        
        base_url = "http://127.0.0.1:8001"
        
        # Test endpoints
        endpoints = [
            "/docs",
            "/redoc", 
            "/api/v1/openapi.json",
            "/api/version",
            "/health"
        ]
        
        for endpoint in endpoints:
            try:
                response = requests.get(f"{base_url}{endpoint}", timeout=5)
                if response.status_code != 200:
                    print(f"❌ Endpoint {endpoint} returned status {response.status_code}")
                    return False
                print(f"✅ Endpoint {endpoint} is accessible")
            except requests.RequestException as e:
                print(f"❌ Error accessing {endpoint}: {e}")
                return False
        
        # Test OpenAPI schema content
        try:
            response = requests.get(f"{base_url}/api/v1/openapi.json", timeout=5)
            schema = response.json()
            
            if schema["info"]["title"] != "Reddit Content Platform API":
                print("❌ OpenAPI schema title mismatch")
                return False
            
            print("✅ OpenAPI schema content is correct")
            
        except Exception as e:
            print(f"❌ Error validating OpenAPI schema: {e}")
            return False
        
        print("✅ All API documentation endpoints are working")
        return True
        
    except ImportError:
        print("⚠️  Skipping server test (uvicorn not available)")
        return True
    except Exception as e:
        print(f"❌ Error testing API server: {e}")
        return False


def test_documentation_generation():
    """Test that documentation can be regenerated."""
    print("🔧 Testing documentation generation...")
    
    try:
        # Run the documentation generator
        result = subprocess.run(
            [sys.executable, "scripts/generate_api_docs.py"],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode != 0:
            print(f"❌ Documentation generation failed: {result.stderr}")
            return False
        
        print("✅ Documentation generation completed successfully")
        return True
        
    except subprocess.TimeoutExpired:
        print("❌ Documentation generation timed out")
        return False
    except Exception as e:
        print(f"❌ Error running documentation generator: {e}")
        return False


def main():
    """Run all documentation tests."""
    print("🚀 Starting API documentation tests...")
    print("=" * 50)
    
    tests = [
        ("OpenAPI Schema", test_openapi_schema),
        ("Postman Collection", test_postman_collection),
        ("Code Examples", test_code_examples),
        ("API Server", test_api_server),
        ("Documentation Generation", test_documentation_generation),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n📋 Running {test_name} test...")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All API documentation tests passed!")
        return 0
    else:
        print("💥 Some API documentation tests failed!")
        return 1


if __name__ == "__main__":
    sys.exit(main())