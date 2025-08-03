#!/usr/bin/env python3
"""
Comprehensive database setup script for Reddit Content Platform.
This script handles database initialization, migration, and verification.
"""

import sys
import os
import asyncio
import logging
import argparse
from typing import Optional

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.db_manager import db_manager
from app.core.database import test_database_connection, close_db_connections
from app.core.config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DatabaseSetup:
    """Database setup and management class."""
    
    def __init__(self):
        self.db_manager = db_manager
    
    async def check_connection(self) -> bool:
        """Check if database connection is working."""
        logger.info("Checking database connection...")
        
        try:
            connection_info = test_database_connection()
            if connection_info["status"] == "healthy":
                logger.info("✓ Database connection successful")
                logger.info(f"  Database version: {connection_info.get('database_version', 'Unknown')}")
                logger.info(f"  Table count: {connection_info.get('table_count', 0)}")
                return True
            else:
                logger.error("✗ Database connection failed")
                logger.error(f"  Error: {connection_info.get('error', 'Unknown error')}")
                return False
        except Exception as e:
            logger.error(f"✗ Connection check failed: {e}")
            return False
    
    async def check_health(self) -> dict:
        """Get comprehensive database health information."""
        logger.info("Performing comprehensive health check...")
        
        try:
            health = await self.db_manager.check_database_health()
            
            logger.info(f"Database Status: {health['status']}")
            logger.info(f"Connection: {'✓' if health['connection'] else '✗'}")
            logger.info(f"Migrations: {'✓' if health['migrations'] else '✗'}")
            logger.info(f"Current revision: {health['current_revision']}")
            logger.info(f"Head revision: {health['head_revision']}")
            
            if health.get('error'):
                logger.error(f"Error: {health['error']}")
            
            return health
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {"status": "error", "error": str(e)}
    
    async def initialize(self, force: bool = False) -> bool:
        """Initialize database with tables and migrations."""
        logger.info("Initializing database...")
        
        try:
            # Check current status
            health = await self.check_health()
            
            if health['status'] == 'healthy' and not force:
                logger.info("Database is already healthy and up to date")
                return True
            
            if force:
                logger.warning("Force initialization requested - this may overwrite existing data")
            
            # Initialize database
            success = self.db_manager.initialize_database()
            
            if success:
                logger.info("✓ Database initialization completed successfully")
                
                # Verify initialization
                health = await self.check_health()
                if health['status'] == 'healthy':
                    logger.info("✓ Database is now healthy and ready to use")
                    return True
                else:
                    logger.error("✗ Database initialization completed but health check failed")
                    return False
            else:
                logger.error("✗ Database initialization failed")
                return False
                
        except Exception as e:
            logger.error(f"Database initialization error: {e}")
            return False
    
    async def migrate(self) -> bool:
        """Run database migrations."""
        logger.info("Running database migrations...")
        
        try:
            # Check current migration status
            current_rev = self.db_manager.get_current_revision()
            head_rev = self.db_manager.get_head_revision()
            
            logger.info(f"Current revision: {current_rev}")
            logger.info(f"Head revision: {head_rev}")
            
            if current_rev == head_rev and current_rev != "Error":
                logger.info("Database is already up to date")
                return True
            
            # Run migrations
            success = self.db_manager.run_migrations()
            
            if success:
                logger.info("✓ Database migrations completed successfully")
                
                # Verify migrations
                new_current = self.db_manager.get_current_revision()
                logger.info(f"New current revision: {new_current}")
                return True
            else:
                logger.error("✗ Database migrations failed")
                return False
                
        except Exception as e:
            logger.error(f"Migration error: {e}")
            return False
    
    async def reset(self, confirm: bool = False) -> bool:
        """Reset database (WARNING: deletes all data)."""
        if not confirm:
            logger.error("Database reset requires explicit confirmation")
            logger.error("Use --confirm flag to confirm data deletion")
            return False
        
        logger.warning("RESETTING DATABASE - THIS WILL DELETE ALL DATA!")
        
        try:
            success = self.db_manager.reset_database()
            
            if success:
                logger.info("✓ Database reset completed successfully")
                return True
            else:
                logger.error("✗ Database reset failed")
                return False
                
        except Exception as e:
            logger.error(f"Database reset error: {e}")
            return False
    
    async def validate(self) -> bool:
        """Validate database migration integrity."""
        logger.info("Validating database migration integrity...")
        
        try:
            validation = self.db_manager.validate_migration_integrity()
            
            logger.info(f"Validation Status: {validation['status']}")
            logger.info(f"Migration count: {validation['migration_count']}")
            
            if validation.get('issues'):
                logger.warning("Issues found:")
                for issue in validation['issues']:
                    logger.warning(f"  - {issue}")
            
            return validation['status'] in ['valid', 'needs_migration']
            
        except Exception as e:
            logger.error(f"Validation error: {e}")
            return False
    
    async def backup_schema(self) -> bool:
        """Backup database schema information."""
        logger.info("Backing up database schema...")
        
        try:
            schema = self.db_manager.backup_database_schema()
            
            if "error" in schema:
                logger.error(f"Schema backup failed: {schema['error']}")
                return False
            
            logger.info("✓ Schema backup completed successfully")
            logger.info(f"  Tables: {len(schema.get('tables', {}))}")
            logger.info(f"  Indexes: {len(schema.get('indexes', {}))}")
            logger.info(f"  Foreign Keys: {len(schema.get('foreign_keys', {}))}")
            
            # Save schema to file
            import json
            from datetime import datetime
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"schema_backup_{timestamp}.json"
            
            with open(filename, 'w') as f:
                json.dump(schema, f, indent=2, default=str)
            
            logger.info(f"Schema saved to: {filename}")
            return True
            
        except Exception as e:
            logger.error(f"Schema backup error: {e}")
            return False
    
    def cleanup(self):
        """Cleanup database connections."""
        try:
            close_db_connections()
            logger.info("Database connections closed")
        except Exception as e:
            logger.error(f"Cleanup error: {e}")


async def main():
    """Main function with command line interface."""
    parser = argparse.ArgumentParser(description="Database setup and management for Reddit Content Platform")
    parser.add_argument("command", choices=[
        "check", "health", "init", "migrate", "reset", "validate", "backup", "status"
    ], help="Command to execute")
    parser.add_argument("--force", action="store_true", help="Force operation (for init)")
    parser.add_argument("--confirm", action="store_true", help="Confirm destructive operations (for reset)")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Display configuration
    logger.info(f"Reddit Content Platform Database Setup")
    logger.info(f"Database URL: {settings.DATABASE_URL}")
    logger.info(f"Command: {args.command}")
    logger.info("-" * 50)
    
    setup = DatabaseSetup()
    success = False
    
    try:
        if args.command == "check":
            success = await setup.check_connection()
        
        elif args.command == "health":
            health = await setup.check_health()
            success = health['status'] in ['healthy', 'needs_migration']
        
        elif args.command == "init":
            success = await setup.initialize(force=args.force)
        
        elif args.command == "migrate":
            success = await setup.migrate()
        
        elif args.command == "reset":
            success = await setup.reset(confirm=args.confirm)
        
        elif args.command == "validate":
            success = await setup.validate()
        
        elif args.command == "backup":
            success = await setup.backup_schema()
        
        elif args.command == "status":
            await setup.check_health()
            await setup.validate()
            success = True
        
        else:
            logger.error(f"Unknown command: {args.command}")
            success = False
    
    except KeyboardInterrupt:
        logger.info("Operation cancelled by user")
        success = False
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        success = False
    finally:
        setup.cleanup()
    
    logger.info("-" * 50)
    logger.info(f"Operation {'COMPLETED' if success else 'FAILED'}")
    
    return success


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)