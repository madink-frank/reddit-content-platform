"""
Database query optimization utilities and enhanced connection management.
"""

import logging
from typing import List, Dict, Any, Optional, Tuple
from contextlib import contextmanager
from sqlalchemy import text, event, Index
from sqlalchemy.orm import Session, joinedload, selectinload, contains_eager
from sqlalchemy.sql import func
from sqlalchemy.engine import Engine
from datetime import datetime, timedelta

from app.core.database import engine, SessionLocal
from app.models.post import Post, Comment
from app.models.keyword import Keyword
from app.models.metric import Metric
from app.models.user import User
from app.models.blog_content import BlogContent

logger = logging.getLogger(__name__)


class QueryOptimizer:
    """Database query optimization utilities."""
    
    @staticmethod
    def create_performance_indexes():
        """Create database indexes for better query performance."""
        try:
            with engine.connect() as conn:
                # Index for posts by keyword_id and created_at (most common query)
                conn.execute(text("""
                    CREATE INDEX IF NOT EXISTS idx_posts_keyword_created 
                    ON posts(keyword_id, created_at DESC)
                """))
                
                # Index for posts by score for trending queries
                conn.execute(text("""
                    CREATE INDEX IF NOT EXISTS idx_posts_score 
                    ON posts(score DESC)
                """))
                
                # Index for posts by subreddit for filtering
                conn.execute(text("""
                    CREATE INDEX IF NOT EXISTS idx_posts_subreddit 
                    ON posts(subreddit)
                """))
                
                # Composite index for post search queries
                conn.execute(text("""
                    CREATE INDEX IF NOT EXISTS idx_posts_search 
                    ON posts(keyword_id, post_created_at DESC, score DESC)
                """))
                
                # Index for comments by post_id
                conn.execute(text("""
                    CREATE INDEX IF NOT EXISTS idx_comments_post_id 
                    ON comments(post_id)
                """))
                
                # Index for metrics by post_id and calculated_at
                conn.execute(text("""
                    CREATE INDEX IF NOT EXISTS idx_metrics_post_calculated 
                    ON metrics(post_id, calculated_at DESC)
                """))
                
                # Index for keywords by user_id and is_active
                conn.execute(text("""
                    CREATE INDEX IF NOT EXISTS idx_keywords_user_active 
                    ON keywords(user_id, is_active)
                """))
                
                # Index for blog_content by keyword_id and generated_at
                conn.execute(text("""
                    CREATE INDEX IF NOT EXISTS idx_blog_content_keyword_generated 
                    ON blog_content(keyword_id, generated_at DESC)
                """))
                
                conn.commit()
                logger.info("Performance indexes created successfully")
                
        except Exception as e:
            logger.error(f"Error creating performance indexes: {e}")
            raise
    
    @staticmethod
    def analyze_query_performance(query_text: str) -> Dict[str, Any]:
        """Analyze query performance using EXPLAIN."""
        try:
            with engine.connect() as conn:
                result = conn.execute(text(f"EXPLAIN ANALYZE {query_text}"))
                return {"query": query_text, "plan": [row for row in result]}
        except Exception as e:
            logger.error(f"Error analyzing query performance: {e}")
            return {"error": str(e)}


class OptimizedPostService:
    """Optimized post service with improved queries."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_posts_with_metrics_optimized(
        self, 
        user_id: int, 
        keyword_id: Optional[int] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Get posts with metrics using optimized query with joins.
        """
        query = (
            self.db.query(Post, Metric)
            .join(Keyword, Post.keyword_id == Keyword.id)
            .outerjoin(Metric, Post.id == Metric.post_id)
            .filter(Keyword.user_id == user_id)
            .options(
                contains_eager(Post.keyword),
                selectinload(Post.comments)
            )
        )
        
        if keyword_id:
            query = query.filter(Post.keyword_id == keyword_id)
        
        # Order by post creation date for better index usage
        query = query.order_by(Post.post_created_at.desc())
        
        results = query.offset(offset).limit(limit).all()
        
        # Transform results to dictionary format
        posts_data = []
        for post, metric in results:
            post_dict = {
                "id": post.id,
                "title": post.title,
                "content": post.content,
                "score": post.score,
                "num_comments": post.num_comments,
                "subreddit": post.subreddit,
                "author": post.author,
                "url": post.url,
                "post_created_at": post.post_created_at,
                "created_at": post.created_at,
                "keyword": post.keyword.keyword if post.keyword else None,
                "metric": {
                    "engagement_score": metric.engagement_score if metric else 0.0,
                    "tfidf_score": metric.tfidf_score if metric else 0.0,
                    "trend_velocity": metric.trend_velocity if metric else 0.0,
                    "calculated_at": metric.calculated_at if metric else None
                }
            }
            posts_data.append(post_dict)
        
        return posts_data
    
    def get_trending_posts_optimized(
        self, 
        user_id: int, 
        hours: int = 24,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Get trending posts using optimized query with window functions.
        """
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        
        # Use raw SQL for complex window function query
        query = text("""
            SELECT 
                p.id,
                p.title,
                p.score,
                p.num_comments,
                p.subreddit,
                p.author,
                p.post_created_at,
                k.keyword,
                m.engagement_score,
                m.tfidf_score,
                -- Calculate trending score using window function
                ROW_NUMBER() OVER (
                    PARTITION BY p.keyword_id 
                    ORDER BY (p.score + p.num_comments * 2) DESC
                ) as rank_in_keyword,
                (p.score + p.num_comments * 2) as trending_score
            FROM posts p
            JOIN keywords k ON p.keyword_id = k.id
            LEFT JOIN metrics m ON p.id = m.post_id
            WHERE k.user_id = :user_id
                AND p.post_created_at >= :cutoff_time
                AND k.is_active = true
            ORDER BY trending_score DESC
            LIMIT :limit
        """)
        
        result = self.db.execute(
            query, 
            {
                "user_id": user_id, 
                "cutoff_time": cutoff_time, 
                "limit": limit
            }
        )
        
        return [dict(row._mapping) for row in result]
    
    def get_post_statistics_optimized(self, user_id: int) -> Dict[str, Any]:
        """
        Get post statistics using optimized aggregation query.
        """
        # Single query to get all statistics
        stats_query = text("""
            SELECT 
                COUNT(p.id) as total_posts,
                AVG(p.score) as avg_score,
                SUM(p.num_comments) as total_comments,
                COUNT(DISTINCT p.subreddit) as unique_subreddits,
                COUNT(DISTINCT p.keyword_id) as active_keywords,
                MAX(p.post_created_at) as latest_post_date,
                AVG(m.engagement_score) as avg_engagement,
                AVG(m.tfidf_score) as avg_tfidf
            FROM posts p
            JOIN keywords k ON p.keyword_id = k.id
            LEFT JOIN metrics m ON p.id = m.post_id
            WHERE k.user_id = :user_id
        """)
        
        result = self.db.execute(stats_query, {"user_id": user_id}).first()
        
        if result:
            return {
                "total_posts": result.total_posts or 0,
                "average_score": float(result.avg_score or 0),
                "total_comments": result.total_comments or 0,
                "unique_subreddits": result.unique_subreddits or 0,
                "active_keywords": result.active_keywords or 0,
                "latest_post_date": result.latest_post_date,
                "average_engagement": float(result.avg_engagement or 0),
                "average_tfidf": float(result.avg_tfidf or 0)
            }
        
        return {}


class OptimizedTrendService:
    """Optimized trend analysis service with better caching."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_keyword_trends_batch(
        self, 
        keyword_ids: List[int], 
        days: int = 7
    ) -> Dict[int, Dict[str, Any]]:
        """
        Get trend data for multiple keywords in a single optimized query.
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        # Batch query for multiple keywords
        trends_query = text("""
            SELECT 
                k.id as keyword_id,
                k.keyword,
                COUNT(p.id) as post_count,
                AVG(p.score) as avg_score,
                AVG(p.num_comments) as avg_comments,
                AVG(m.engagement_score) as avg_engagement,
                AVG(m.tfidf_score) as avg_tfidf,
                AVG(m.trend_velocity) as avg_velocity,
                MAX(p.post_created_at) as latest_post,
                -- Calculate trend direction
                CASE 
                    WHEN AVG(m.trend_velocity) > 0.1 THEN 'rising'
                    WHEN AVG(m.trend_velocity) < -0.1 THEN 'falling'
                    ELSE 'stable'
                END as trend_direction
            FROM keywords k
            LEFT JOIN posts p ON k.id = p.keyword_id 
                AND p.post_created_at >= :cutoff_date
            LEFT JOIN metrics m ON p.id = m.post_id
            WHERE k.id = ANY(:keyword_ids)
            GROUP BY k.id, k.keyword
            ORDER BY avg_engagement DESC NULLS LAST
        """)
        
        result = self.db.execute(
            trends_query, 
            {
                "keyword_ids": keyword_ids, 
                "cutoff_date": cutoff_date
            }
        )
        
        trends_data = {}
        for row in result:
            trends_data[row.keyword_id] = {
                "keyword": row.keyword,
                "post_count": row.post_count or 0,
                "avg_score": float(row.avg_score or 0),
                "avg_comments": float(row.avg_comments or 0),
                "avg_engagement": float(row.avg_engagement or 0),
                "avg_tfidf": float(row.avg_tfidf or 0),
                "avg_velocity": float(row.avg_velocity or 0),
                "latest_post": row.latest_post,
                "trend_direction": row.trend_direction,
                "analyzed_at": datetime.utcnow().isoformat()
            }
        
        return trends_data


class ConnectionPoolOptimizer:
    """Database connection pool optimization."""
    
    @staticmethod
    def optimize_connection_pool():
        """Optimize database connection pool settings."""
        # These settings are applied during engine creation
        # but can be monitored and adjusted
        pool_info = {
            "pool_size": engine.pool.size(),
            "checked_out": engine.pool.checkedout(),
            "overflow": engine.pool.overflow(),
            "checked_in": engine.pool.checkedin()
        }
        
        logger.info(f"Connection pool status: {pool_info}")
        return pool_info
    
    @staticmethod
    @contextmanager
    def get_optimized_session():
        """Get database session with optimized settings."""
        session = SessionLocal()
        try:
            # Set session-level optimizations
            session.execute(text("SET statement_timeout = '30s'"))
            session.execute(text("SET lock_timeout = '10s'"))
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Database session error: {e}")
            raise
        finally:
            session.close()


# Query performance monitoring
class QueryPerformanceMonitor:
    """Monitor and log slow queries."""
    
    def __init__(self, slow_query_threshold: float = 1.0):
        self.slow_query_threshold = slow_query_threshold
        self.query_stats = {}
    
    def log_query_performance(self, query: str, execution_time: float):
        """Log query performance metrics."""
        if execution_time > self.slow_query_threshold:
            logger.warning(
                f"Slow query detected: {execution_time:.3f}s - {query[:100]}..."
            )
        
        # Update query statistics
        if query not in self.query_stats:
            self.query_stats[query] = {
                "count": 0,
                "total_time": 0.0,
                "avg_time": 0.0,
                "max_time": 0.0
            }
        
        stats = self.query_stats[query]
        stats["count"] += 1
        stats["total_time"] += execution_time
        stats["avg_time"] = stats["total_time"] / stats["count"]
        stats["max_time"] = max(stats["max_time"], execution_time)
    
    def get_performance_report(self) -> Dict[str, Any]:
        """Get query performance report."""
        return {
            "total_queries": len(self.query_stats),
            "slow_queries": [
                {
                    "query": query[:100] + "..." if len(query) > 100 else query,
                    "stats": stats
                }
                for query, stats in self.query_stats.items()
                if stats["avg_time"] > self.slow_query_threshold
            ],
            "top_queries_by_time": sorted(
                [
                    {
                        "query": query[:100] + "..." if len(query) > 100 else query,
                        "avg_time": stats["avg_time"],
                        "count": stats["count"]
                    }
                    for query, stats in self.query_stats.items()
                ],
                key=lambda x: x["avg_time"],
                reverse=True
            )[:10]
        }


# Global performance monitor instance
query_monitor = QueryPerformanceMonitor()


# Event listener for query performance monitoring
@event.listens_for(Engine, "before_cursor_execute")
def receive_before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    context._query_start_time = datetime.utcnow()


@event.listens_for(Engine, "after_cursor_execute")
def receive_after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    if hasattr(context, '_query_start_time'):
        execution_time = (datetime.utcnow() - context._query_start_time).total_seconds()
        query_monitor.log_query_performance(statement, execution_time)