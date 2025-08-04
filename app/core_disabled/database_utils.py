"""
Database utility functions for initialization, seeding, and maintenance.
"""

import logging
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.core.database import get_db_session, DatabaseManager
from app.models import User, Keyword, Post, Comment, Metric, BlogContent, ProcessLog

logger = logging.getLogger(__name__)


class DatabaseSeeder:
    """
    Database seeding utilities for development and testing.
    """
    
    @staticmethod
    def create_test_user(
        name: str = "Test User",
        email: str = "test@example.com",
        oauth_provider: str = "google",
        oauth_id: str = "test_oauth_id"
    ) -> Optional[User]:
        """
        Create a test user for development/testing purposes.
        """
        try:
            with get_db_session() as db:
                # Check if user already exists
                existing_user = db.query(User).filter(User.email == email).first()
                if existing_user:
                    logger.info(f"Test user with email {email} already exists")
                    return existing_user
                
                user = User(
                    name=name,
                    email=email,
                    oauth_provider=oauth_provider,
                    oauth_id=oauth_id
                )
                db.add(user)
                db.commit()
                db.refresh(user)
                logger.info(f"Created test user: {user.email}")
                return user
        except IntegrityError as e:
            logger.error(f"Error creating test user: {e}")
            return None
    
    @staticmethod
    def create_test_keywords(user_id: int, keywords: List[str]) -> List[Keyword]:
        """
        Create test keywords for a user.
        """
        created_keywords = []
        try:
            with get_db_session() as db:
                for keyword_text in keywords:
                    # Check if keyword already exists for this user
                    existing_keyword = db.query(Keyword).filter(
                        Keyword.user_id == user_id,
                        Keyword.keyword == keyword_text
                    ).first()
                    
                    if not existing_keyword:
                        keyword = Keyword(
                            user_id=user_id,
                            keyword=keyword_text,
                            is_active=True
                        )
                        db.add(keyword)
                        created_keywords.append(keyword)
                
                db.commit()
                for keyword in created_keywords:
                    db.refresh(keyword)
                
                logger.info(f"Created {len(created_keywords)} test keywords")
                return created_keywords
        except IntegrityError as e:
            logger.error(f"Error creating test keywords: {e}")
            return []
    
    @staticmethod
    def seed_development_data():
        """
        Seed database with development data.
        """
        logger.info("Starting development data seeding...")
        
        # Create test user
        user = DatabaseSeeder.create_test_user()
        if not user:
            logger.error("Failed to create test user")
            return
        
        # Create test keywords
        test_keywords = ["python", "fastapi", "reddit", "machine learning", "web development"]
        keywords = DatabaseSeeder.create_test_keywords(user.id, test_keywords)
        
        logger.info("Development data seeding completed")


class DatabaseMaintenance:
    """
    Database maintenance utilities.
    """
    
    @staticmethod
    def cleanup_old_process_logs(days_old: int = 30) -> int:
        """
        Clean up process logs older than specified days.
        Returns number of deleted records.
        """
        try:
            with get_db_session() as db:
                cutoff_date = datetime.utcnow() - timedelta(days=days_old)
                deleted_count = db.query(ProcessLog).filter(
                    ProcessLog.created_at < cutoff_date
                ).delete()
                db.commit()
                logger.info(f"Cleaned up {deleted_count} old process logs")
                return deleted_count
        except Exception as e:
            logger.error(f"Error cleaning up process logs: {e}")
            return 0
    
    @staticmethod
    def get_database_stats() -> Dict[str, Any]:
        """
        Get database statistics for monitoring.
        """
        stats = {}
        try:
            with get_db_session() as db:
                stats['users_count'] = db.query(User).count()
                stats['keywords_count'] = db.query(Keyword).count()
                stats['posts_count'] = db.query(Post).count()
                stats['comments_count'] = db.query(Comment).count()
                stats['metrics_count'] = db.query(Metric).count()
                stats['blog_contents_count'] = db.query(BlogContent).count()
                stats['process_logs_count'] = db.query(ProcessLog).count()
                
                # Active keywords
                stats['active_keywords_count'] = db.query(Keyword).filter(
                    Keyword.is_active == True
                ).count()
                
                # Recent posts (last 7 days)
                from datetime import timedelta
                week_ago = datetime.utcnow() - timedelta(days=7)
                stats['recent_posts_count'] = db.query(Post).filter(
                    Post.created_at >= week_ago
                ).count()
                
                logger.info("Database statistics retrieved successfully")
        except Exception as e:
            logger.error(f"Error retrieving database statistics: {e}")
            stats['error'] = str(e)
        
        return stats
    
    @staticmethod
    def validate_data_integrity() -> Dict[str, Any]:
        """
        Validate database data integrity.
        Returns validation results.
        """
        results = {
            'valid': True,
            'issues': [],
            'warnings': []
        }
        
        try:
            with get_db_session() as db:
                # Check for orphaned keywords (users that don't exist)
                orphaned_keywords = db.query(Keyword).filter(
                    ~Keyword.user_id.in_(db.query(User.id))
                ).count()
                
                if orphaned_keywords > 0:
                    results['valid'] = False
                    results['issues'].append(f"Found {orphaned_keywords} orphaned keywords")
                
                # Check for orphaned posts (keywords that don't exist)
                orphaned_posts = db.query(Post).filter(
                    ~Post.keyword_id.in_(db.query(Keyword.id))
                ).count()
                
                if orphaned_posts > 0:
                    results['valid'] = False
                    results['issues'].append(f"Found {orphaned_posts} orphaned posts")
                
                # Check for duplicate Reddit IDs
                from sqlalchemy import text
                duplicate_posts = db.execute(text("""
                    SELECT reddit_id, COUNT(*) as count 
                    FROM posts 
                    GROUP BY reddit_id 
                    HAVING COUNT(*) > 1
                """)).fetchall()
                
                if duplicate_posts:
                    results['warnings'].append(f"Found {len(duplicate_posts)} duplicate Reddit post IDs")
                
                logger.info("Data integrity validation completed")
        except Exception as e:
            logger.error(f"Error during data integrity validation: {e}")
            results['valid'] = False
            results['issues'].append(f"Validation error: {str(e)}")
        
        return results


def initialize_database():
    """
    Initialize database with tables and basic setup.
    """
    logger.info("Initializing database...")
    
    # Check database connection
    if not DatabaseManager.check_connection():
        logger.error("Database connection failed")
        return False
    
    # Create all tables
    try:
        DatabaseManager.create_all_tables()
        logger.info("Database initialization completed successfully")
        return True
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        return False


if __name__ == "__main__":
    # This allows running the script directly for database setup
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "init":
            initialize_database()
        elif command == "seed":
            DatabaseSeeder.seed_development_data()
        elif command == "stats":
            stats = DatabaseMaintenance.get_database_stats()
            print("Database Statistics:")
            for key, value in stats.items():
                print(f"  {key}: {value}")
        elif command == "validate":
            results = DatabaseMaintenance.validate_data_integrity()
            print("Data Integrity Validation:")
            print(f"  Valid: {results['valid']}")
            if results['issues']:
                print("  Issues:")
                for issue in results['issues']:
                    print(f"    - {issue}")
            if results['warnings']:
                print("  Warnings:")
                for warning in results['warnings']:
                    print(f"    - {warning}")
        else:
            print("Available commands: init, seed, stats, validate")
    else:
        print("Usage: python app/core/database_utils.py <command>")
        print("Available commands: init, seed, stats, validate")