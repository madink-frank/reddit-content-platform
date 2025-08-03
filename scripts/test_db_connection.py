#!/usr/bin/env python3
"""
Simple database connection test script.
This script tests the database connection and basic functionality.
"""

import sys
import os
import asyncio
import logging

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import test_database_connection, check_database_health
from app.core.db_manager import db_manager, check_db_health
from app.core.config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def main():
    """Test database connection and functionality."""
    print("=== Database Connection Test ===\n")
    
    # Display configuration
    print(f"Database URL: {settings.DATABASE_URL}")
    print(f"Project: {settings.PROJECT_NAME}")
    print()
    
    # Test basic database connection
    print("1. Testing basic database connection...")
    try:
        connection_info = test_database_connection()
        if connection_info["status"] == "healthy":
            print("✓ Database connection successful")
            print(f"  Database version: {connection_info.get('database_version', 'Unknown')}")
            print(f"  Table count: {connection_info.get('table_count', 0)}")
            print(f"  Connection pool size: {connection_info.get('connection_pool_size', 0)}")
        else:
            print("✗ Database connection failed")
            print(f"  Error: {connection_info.get('error', 'Unknown error')}")
    except Exception as e:
        print(f"✗ Connection test failed: {e}")
    
    print()
    
    # Test database health check
    print("2. Testing database health check...")
    try:
        is_healthy = await check_database_health()
        print(f"✓ Health check result: {'Healthy' if is_healthy else 'Unhealthy'}")
    except Exception as e:
        print(f"✗ Health check failed: {e}")
    
    print()
    
    # Test comprehensive health check
    print("3. Testing comprehensive health check...")
    try:
        health_info = await check_db_health()
        print(f"✓ Comprehensive health check completed")
        print(f"  Status: {health_info.get('status', 'Unknown')}")
        print(f"  Connection: {health_info.get('connection', False)}")
        print(f"  Migrations: {health_info.get('migrations', False)}")
        print(f"  Current revision: {health_info.get('current_revision', 'Unknown')}")
        print(f"  Head revision: {health_info.get('head_revision', 'Unknown')}")
        if health_info.get('error'):
            print(f"  Error: {health_info['error']}")
    except Exception as e:
        print(f"✗ Comprehensive health check failed: {e}")
    
    print()
    
    # Test migration status
    print("4. Testing migration status...")
    try:
        current_rev = db_manager.get_current_revision()
        head_rev = db_manager.get_head_revision()
        up_to_date = db_manager.is_database_up_to_date()
        
        print(f"✓ Migration status checked")
        print(f"  Current revision: {current_rev}")
        print(f"  Head revision: {head_rev}")
        print(f"  Up to date: {up_to_date}")
        
        if current_rev == "Error":
            print("  Note: Cannot connect to database to check current revision")
        elif not up_to_date and current_rev != "Error":
            print("  Warning: Database needs migration")
    except Exception as e:
        print(f"✗ Migration status check failed: {e}")
    
    print()
    
    # Test migration validation
    print("5. Testing migration validation...")
    try:
        validation = db_manager.validate_migration_integrity()
        print(f"✓ Migration validation completed")
        print(f"  Status: {validation.get('status', 'Unknown')}")
        print(f"  Migration count: {validation.get('migration_count', 0)}")
        if validation.get('issues'):
            print(f"  Issues: {validation['issues']}")
    except Exception as e:
        print(f"✗ Migration validation failed: {e}")
    
    print()
    print("=== Test Complete ===")


if __name__ == "__main__":
    asyncio.run(main())