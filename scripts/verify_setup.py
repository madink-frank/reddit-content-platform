#!/usr/bin/env python3
"""
Script to verify the basic project setup is working correctly.
"""

import sys
import os
import importlib.util
from pathlib import Path

def check_file_exists(file_path: str) -> bool:
    """Check if a file exists."""
    return Path(file_path).exists()

def check_import(module_name: str) -> bool:
    """Check if a module can be imported."""
    try:
        importlib.import_module(module_name)
        return True
    except ImportError:
        return False

def main():
    """Main verification function."""
    print("🔍 Verifying Reddit Content Platform Setup...")
    print("=" * 50)
    
    # Check core files
    core_files = [
        "app/__init__.py",
        "app/main.py",
        "app/core/config.py",
        "app/core/database.py",
        "app/core/celery_app.py",
        "app/core/security.py",
        "app/core/redis_client.py",
        "app/core/logging.py",
        "app/core/metrics.py",
        "app/core/openapi_config.py",
        "requirements.txt",
        "docker-compose.yml",
        "Dockerfile",
        ".env",
        ".env.example"
    ]
    
    print("📁 Checking core files...")
    missing_files = []
    for file_path in core_files:
        if check_file_exists(file_path):
            print(f"  ✅ {file_path}")
        else:
            print(f"  ❌ {file_path}")
            missing_files.append(file_path)
    
    # Check imports
    print("\n📦 Checking core imports...")
    core_imports = [
        "app.main",
        "app.core.config",
        "app.core.database",
        "app.core.celery_app",
        "app.core.security",
        "app.core.redis_client",
        "app.core.logging",
        "app.core.metrics",
        "app.core.openapi_config"
    ]
    
    import_failures = []
    for module in core_imports:
        if check_import(module):
            print(f"  ✅ {module}")
        else:
            print(f"  ❌ {module}")
            import_failures.append(module)
    
    # Test FastAPI app
    print("\n🚀 Testing FastAPI application...")
    try:
        from app.main import app
        from fastapi.testclient import TestClient
        
        client = TestClient(app)
        response = client.get("/health")
        
        if response.status_code == 200:
            print("  ✅ Health check endpoint working")
            print(f"     Response: {response.json()}")
        else:
            print(f"  ❌ Health check failed: {response.status_code}")
            
        # Test API root
        response = client.get("/api/v1/")
        if response.status_code == 200:
            print("  ✅ API v1 root endpoint working")
        else:
            print(f"  ❌ API v1 root failed: {response.status_code}")
            
    except Exception as e:
        print(f"  ❌ FastAPI test failed: {e}")
    
    # Summary
    print("\n" + "=" * 50)
    if missing_files or import_failures:
        print("❌ Setup verification FAILED")
        if missing_files:
            print(f"   Missing files: {missing_files}")
        if import_failures:
            print(f"   Import failures: {import_failures}")
        sys.exit(1)
    else:
        print("✅ Setup verification PASSED")
        print("🎉 Reddit Content Platform is ready for development!")

if __name__ == "__main__":
    main()