#!/usr/bin/env python3
"""
Database initialization script for Reddit Content Platform.
This script can be used to initialize the database during deployment or development.
"""

import sys
import os
import asyncio
import logging

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.db_manager import db_manager
from app.core.config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def main():
    """Main function to initialize the database."""
    logger.info("Starting database initialization...")
    logger.info(f"Database URL: {settings.DATABASE_URL}")
    
    try:
        # Check current database health
        logger.info("Checking database health...")
        health = await db_manager.check_database_health()
        logger.info(f"Database status: {health['status']}")
        
        if health['status'] == 'healthy':
            logger.info("Database is already healthy and up to date")
            return True
        
        # Initialize database if needed
        if health['status'] in ['unhealthy', 'needs_migration', 'unknown']:
            logger.info("Initializing database...")
            success = db_manager.initialize_database()
            
            if success:
                logger.info("Database initialization completed successfully")
                
                # Verify initialization
                health = await db_manager.check_database_health()
                logger.info(f"Post-initialization status: {health['status']}")
                
                if health['status'] == 'healthy':
                    logger.info("Database is now healthy and ready to use")
                    return True
                else:
                    logger.error("Database initialization completed but health check failed")
                    return False
            else:
                logger.error("Database initialization failed")
                return False
        
        return True
        
    except Exception as e:
        logger.error(f"Error during database initialization: {e}")
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)