"""
Database configuration and session management.
Supports both SQLite (development) and PostgreSQL (production/Supabase).
"""

import logging
from contextlib import contextmanager
from typing import Generator

from sqlalchemy import create_engine, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from sqlalchemy.exc import SQLAlchemyError

from app.core.config import settings
from app.core.db_logging import setup_query_logging

logger = logging.getLogger(__name__)

# Create database engine based on DATABASE_URL
if settings.DATABASE_URL.startswith("sqlite"):
    # SQLite configuration for development
    engine = create_engine(
        settings.DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=settings.ENVIRONMENT == "development"
    )
else:
    # PostgreSQL configuration for production (including Supabase)
    engine = create_engine(
        settings.DATABASE_URL,
        pool_pre_ping=True,
        pool_recycle=300,
        pool_size=10,
        max_overflow=20,
        echo=settings.ENVIRONMENT == "development",
        # Supabase-specific connection parameters
        connect_args={
            "sslmode": "require",
            "application_name": "reddit-content-platform"
        } if "supabase.co" in settings.DATABASE_URL else {}
    )

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create declarative base for models
Base = declarative_base()

# Setup database query logging
setup_query_logging()


def get_db() -> Generator[Session, None, None]:
    """
    Dependency to get database session.
    Ensures proper session cleanup.
    """
    db = SessionLocal()
    try:
        yield db
    except SQLAlchemyError as e:
        logger.error(f"Database error occurred: {e}")
        db.rollback()
        raise
    finally:
        db.close()


@contextmanager
def get_db_session() -> Generator[Session, None, None]:
    """
    Context manager for database sessions.
    Useful for background tasks and services.
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except SQLAlchemyError as e:
        logger.error(f"Database error occurred: {e}")
        db.rollback()
        raise
    finally:
        db.close()


class DatabaseManager:
    """
    Database management utilities for advanced operations.
    """
    
    @staticmethod
    def create_all_tables():
        """
        Create all tables defined in models.
        Used for testing and initial setup.
        """
        try:
            # Import all models to ensure they are registered
            from app.models import (
                User, Keyword, Post, Comment, Metric, BlogContent, ProcessLog
            )
            Base.metadata.create_all(bind=engine)
            logger.info("All database tables created successfully")
        except Exception as e:
            logger.error(f"Error creating database tables: {e}")
            raise
    
    @staticmethod
    def drop_all_tables():
        """
        Drop all tables. Use with caution!
        Primarily for testing environments.
        """
        try:
            Base.metadata.drop_all(bind=engine)
            logger.info("All database tables dropped successfully")
        except Exception as e:
            logger.error(f"Error dropping database tables: {e}")
            raise
    
    @staticmethod
    def check_connection() -> bool:
        """
        Check if database connection is working.
        Returns True if connection is successful, False otherwise.
        """
        try:
            from sqlalchemy import text
            with engine.connect() as connection:
                connection.execute(text("SELECT 1"))
            logger.info("Database connection check successful")
            return True
        except Exception as e:
            logger.error(f"Database connection check failed: {e}")
            return False


# Event listeners for connection management
@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    """
    Set SQLite pragmas for better performance and data integrity.
    Only applies to SQLite connections.
    """
    if settings.DATABASE_URL.startswith("sqlite"):
        cursor = dbapi_connection.cursor()
        # Enable foreign key constraints
        cursor.execute("PRAGMA foreign_keys=ON")
        # Set journal mode to WAL for better concurrency
        cursor.execute("PRAGMA journal_mode=WAL")
        # Set synchronous mode to NORMAL for better performance
        cursor.execute("PRAGMA synchronous=NORMAL")
        cursor.close()


@event.listens_for(engine, "checkout")
def receive_checkout(dbapi_connection, connection_record, connection_proxy):
    """
    Log database connection checkout for monitoring.
    """
    logger.debug("Database connection checked out from pool")


@event.listens_for(engine, "checkin")
def receive_checkin(dbapi_connection, connection_record):
    """
    Log database connection checkin for monitoring.
    """
    logger.debug("Database connection returned to pool")