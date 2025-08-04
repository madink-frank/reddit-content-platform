"""
Trend Analysis Service for TF-IDF based trend analysis and metrics calculation.
"""

import logging
import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple, Any
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc, func

from app.models.post import Post, Comment
from app.models.metric import Metric
from app.models.keyword import Keyword
from app.core.database import get_db
from app.core.redis_client import redis_client, cache_manager
from app.core.logging import get_logger, ErrorCategory

logger = get_logger(__name__)


class TrendAnalysisService:
    """
    Service for analyzing trends using TF-IDF algorithm and calculating engagement metrics.
    Enhanced with comprehensive caching and trend history tracking.
    """
    
    def __init__(self):
        self.redis_client = redis_client.redis  # Use synchronous Redis client
        self.cache_manager = cache_manager
        self.tfidf_vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words='english',
            ngram_range=(1, 2),
            min_df=1,  # Changed from 2 to 1 to handle small document sets
            max_df=0.8
        )
        
        # Cache expiration times (in seconds)
        self.TREND_DATA_CACHE_TTL = 1800  # 30 minutes
        self.TREND_HISTORY_CACHE_TTL = 3600  # 1 hour
        self.KEYWORD_RANKING_CACHE_TTL = 900  # 15 minutes
        self.TREND_SUMMARY_CACHE_TTL = 600  # 10 minutes
    
    async def analyze_keyword_trends(self, keyword_id: int, db: Session, force_refresh: bool = False) -> Dict[str, Any]:
        """
        Analyze trends for a specific keyword using TF-IDF algorithm.
        Enhanced with comprehensive caching and trend history tracking.
        
        Args:
            keyword_id: ID of the keyword to analyze
            db: Database session
            force_refresh: Force refresh of cached data
            
        Returns:
            Dictionary containing trend analysis results
        """
        try:
            # Check cache first unless force refresh is requested
            if not force_refresh:
                cached_data = await self.get_cached_trend_data(keyword_id)
                if cached_data:
                    logger.info(f"Returning cached trend data for keyword_id: {keyword_id}")
                    return cached_data
            
            # Get posts for the keyword
            posts = db.query(Post).filter(Post.keyword_id == keyword_id).all()
            
            if not posts:
                logger.warning(f"No posts found for keyword_id: {keyword_id}")
                return self._create_empty_trend_data(keyword_id)
            
            # Calculate TF-IDF scores
            tfidf_scores = self._calculate_tfidf_scores(posts)
            
            # Calculate engagement scores
            engagement_scores = self._calculate_engagement_scores(posts)
            
            # Calculate trend velocity
            trend_velocity = self._calculate_trend_velocity(keyword_id, db)
            
            # Calculate additional metrics
            sentiment_scores = self._calculate_sentiment_scores(posts)
            virality_scores = self._calculate_virality_scores(posts, db)
            
            # Store metrics in database
            await self._store_metrics(posts, tfidf_scores, engagement_scores, trend_velocity, sentiment_scores, virality_scores, db)
            
            # Create comprehensive trend data
            trend_data = {
                "keyword_id": keyword_id,
                "avg_tfidf_score": float(np.mean(list(tfidf_scores.values())) if tfidf_scores else 0.0),
                "avg_engagement_score": float(np.mean(list(engagement_scores.values())) if engagement_scores else 0.0),
                "avg_sentiment_score": float(np.mean(list(sentiment_scores.values())) if sentiment_scores else 0.0),
                "avg_virality_score": float(np.mean(list(virality_scores.values())) if virality_scores else 0.0),
                "trend_velocity": float(trend_velocity),
                "total_posts": len(posts),
                "analyzed_at": datetime.utcnow().isoformat(),
                "cache_expires_at": (datetime.utcnow() + timedelta(seconds=self.TREND_DATA_CACHE_TTL)).isoformat(),
                "top_keywords": self._extract_top_keywords(posts),
                "engagement_distribution": self._calculate_engagement_distribution(engagement_scores),
                "trend_direction": self._determine_trend_direction(trend_velocity),
                "confidence_score": self._calculate_confidence_score(len(posts), trend_velocity)
            }
            
            # Cache the results
            await self.cache_trend_data(keyword_id, trend_data)
            
            # Store in trend history
            await self._store_trend_history(keyword_id, trend_data, db)
            
            logger.info(f"Trend analysis completed for keyword_id: {keyword_id}")
            return trend_data
            
        except Exception as e:
            logger.error(
                "Error analyzing trends",
                error_category=ErrorCategory.BUSINESS_LOGIC,
                alert_level="medium",
                operation="trend_analysis",
                keyword_id=keyword_id,
                error=str(e),
                exc_info=True
            )
            raise
    
    def _calculate_tfidf_scores(self, posts: List[Post]) -> Dict[int, float]:
        """
        Calculate TF-IDF scores for posts.
        
        Args:
            posts: List of Post objects
            
        Returns:
            Dictionary mapping post_id to TF-IDF score
        """
        if not posts:
            return {}
        
        try:
            # Prepare text corpus
            documents = []
            post_ids = []
            
            for post in posts:
                # Combine title and content for analysis
                text = f"{post.title} {post.content or ''}"
                documents.append(text)
                post_ids.append(post.id)
            
            # Calculate TF-IDF matrix
            tfidf_matrix = self.tfidf_vectorizer.fit_transform(documents)
            
            # Calculate document scores (sum of TF-IDF values for each document)
            doc_scores = np.array(tfidf_matrix.sum(axis=1)).flatten()
            
            # Normalize scores to 0-1 range
            if doc_scores.max() > 0:
                doc_scores = doc_scores / doc_scores.max()
            
            # Create mapping of post_id to TF-IDF score
            tfidf_scores = {}
            for i, post_id in enumerate(post_ids):
                tfidf_scores[post_id] = float(doc_scores[i])
            
            return tfidf_scores
            
        except Exception as e:
            logger.error(f"Error calculating TF-IDF scores: {str(e)}")
            return {}
    
    def _calculate_engagement_scores(self, posts: List[Post]) -> Dict[int, float]:
        """
        Calculate engagement scores based on Reddit metrics.
        
        Args:
            posts: List of Post objects
            
        Returns:
            Dictionary mapping post_id to engagement score
        """
        engagement_scores = {}
        
        if not posts:
            return engagement_scores
        
        try:
            # Get max values for normalization
            max_score = max(post.score for post in posts) if posts else 1
            max_comments = max(post.num_comments for post in posts) if posts else 1
            
            for post in posts:
                # Calculate engagement score using weighted formula
                # Score weight: 0.6, Comments weight: 0.4
                normalized_score = post.score / max_score if max_score > 0 else 0
                normalized_comments = post.num_comments / max_comments if max_comments > 0 else 0
                
                engagement_score = (0.6 * normalized_score) + (0.4 * normalized_comments)
                engagement_scores[post.id] = float(engagement_score)
            
            return engagement_scores
            
        except Exception as e:
            logger.error(f"Error calculating engagement scores: {str(e)}")
            return {}
    
    def _calculate_trend_velocity(self, keyword_id: int, db: Session) -> float:
        """
        Calculate trend velocity based on recent metrics history.
        
        Args:
            keyword_id: ID of the keyword
            db: Database session
            
        Returns:
            Trend velocity score
        """
        try:
            # Get recent metrics (last 7 days)
            seven_days_ago = datetime.utcnow() - timedelta(days=7)
            
            recent_metrics = db.query(Metric).join(Post).filter(
                and_(
                    Post.keyword_id == keyword_id,
                    Metric.calculated_at >= seven_days_ago
                )
            ).order_by(desc(Metric.calculated_at)).all()
            
            if len(recent_metrics) < 2:
                return 0.0
            
            # Calculate velocity as change in average engagement over time
            mid_point = len(recent_metrics) // 2
            recent_half = recent_metrics[:mid_point]
            older_half = recent_metrics[mid_point:]
            
            recent_avg = np.mean([m.engagement_score for m in recent_half])
            older_avg = np.mean([m.engagement_score for m in older_half])
            
            # Calculate velocity (rate of change)
            velocity = (recent_avg - older_avg) / len(recent_metrics) * 100
            
            return float(velocity)
            
        except Exception as e:
            logger.error(f"Error calculating trend velocity: {str(e)}")
            return 0.0
    
    async def _store_metrics(
        self, 
        posts: List[Post], 
        tfidf_scores: Dict[int, float], 
        engagement_scores: Dict[int, float], 
        trend_velocity: float,
        sentiment_scores: Dict[int, float],
        virality_scores: Dict[int, float],
        db: Session
    ):
        """
        Store calculated metrics in the database.
        
        Args:
            posts: List of Post objects
            tfidf_scores: TF-IDF scores by post_id
            engagement_scores: Engagement scores by post_id
            trend_velocity: Calculated trend velocity
            sentiment_scores: Sentiment scores by post_id
            virality_scores: Virality scores by post_id
            db: Database session
        """
        try:
            current_time = datetime.utcnow()
            
            for post in posts:
                # Check if metric already exists for this post
                existing_metric = db.query(Metric).filter(Metric.post_id == post.id).first()
                
                if existing_metric:
                    # Update existing metric
                    existing_metric.engagement_score = engagement_scores.get(post.id, 0.0)
                    existing_metric.tfidf_score = tfidf_scores.get(post.id, 0.0)
                    existing_metric.trend_velocity = trend_velocity
                    existing_metric.sentiment_score = sentiment_scores.get(post.id, 0.0)
                    existing_metric.virality_score = virality_scores.get(post.id, 0.0)
                    existing_metric.calculated_at = current_time
                else:
                    # Create new metric
                    metric = Metric(
                        post_id=post.id,
                        engagement_score=engagement_scores.get(post.id, 0.0),
                        tfidf_score=tfidf_scores.get(post.id, 0.0),
                        trend_velocity=trend_velocity,
                        sentiment_score=sentiment_scores.get(post.id, 0.0),
                        virality_score=virality_scores.get(post.id, 0.0),
                        calculated_at=current_time
                    )
                    db.add(metric)
            
            db.commit()
            logger.info(f"Stored metrics for {len(posts)} posts")
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error storing metrics: {str(e)}")
            raise
    
    async def get_cached_trend_data(self, keyword_id: int) -> Optional[Dict[str, Any]]:
        """
        Get cached trend data for a keyword.
        
        Args:
            keyword_id: ID of the keyword
            
        Returns:
            Cached trend data or None if not found
        """
        try:
            return await self.cache_manager.get_cached_trend_data(keyword_id)
        except Exception as e:
            logger.error(f"Error getting cached trend data for keyword_id {keyword_id}: {str(e)}")
            return None
    
    async def cache_trend_data(self, keyword_id: int, trend_data: Dict[str, Any]) -> bool:
        """
        Cache trend data for a keyword.
        
        Args:
            keyword_id: ID of the keyword
            trend_data: Trend analysis data to cache
            
        Returns:
            True if caching was successful
        """
        try:
            return await self.cache_manager.cache_trend_data(keyword_id, trend_data, self.TREND_DATA_CACHE_TTL)
        except Exception as e:
            logger.error(f"Error caching trend data for keyword_id {keyword_id}: {str(e)}")
            return False
    
    async def invalidate_trend_cache(self, keyword_id: int) -> bool:
        """
        Invalidate cached trend data for a keyword.
        
        Args:
            keyword_id: ID of the keyword
            
        Returns:
            True if invalidation was successful
        """
        try:
            cache_key = f"trend:keyword:{keyword_id}"
            return await self.cache_manager.redis.delete(cache_key)
        except Exception as e:
            logger.error(f"Error invalidating trend cache for keyword_id {keyword_id}: {str(e)}")
            return False
    
    async def get_keyword_importance_ranking(self, user_id: int, db: Session, force_refresh: bool = False) -> List[Dict]:
        """
        Get keyword importance ranking based on TF-IDF and engagement scores.
        Enhanced with caching.
        
        Args:
            user_id: ID of the user
            db: Database session
            force_refresh: Force refresh of cached data
            
        Returns:
            List of keywords ranked by importance
        """
        try:
            # Check cache first unless force refresh is requested
            if not force_refresh:
                cache_key = f"keyword_ranking:user:{user_id}"
                cached_rankings = await self.cache_manager.redis.get_json(cache_key)
                if cached_rankings:
                    logger.info(f"Returning cached keyword rankings for user_id: {user_id}")
                    return cached_rankings
            
            # Get user's keywords with their metrics
            keywords_query = db.query(Keyword).filter(Keyword.user_id == user_id).all()
            
            keyword_rankings = []
            
            for keyword in keywords_query:
                # Get average metrics for this keyword
                avg_metrics = db.query(
                    func.avg(Metric.tfidf_score).label('avg_tfidf'),
                    func.avg(Metric.engagement_score).label('avg_engagement'),
                    func.avg(Metric.trend_velocity).label('avg_velocity'),
                    func.avg(Metric.sentiment_score).label('avg_sentiment'),
                    func.avg(Metric.virality_score).label('avg_virality'),
                    func.count(Metric.id).label('total_posts')
                ).join(Post).filter(Post.keyword_id == keyword.id).first()
                
                if avg_metrics and avg_metrics.total_posts > 0:
                    # Calculate importance score with enhanced metrics
                    importance_score = (
                        (avg_metrics.avg_tfidf or 0) * 0.3 +
                        (avg_metrics.avg_engagement or 0) * 0.3 +
                        abs(avg_metrics.avg_velocity or 0) * 0.2 +
                        abs(avg_metrics.avg_sentiment or 0) * 0.1 +
                        (avg_metrics.avg_virality or 0) * 0.1
                    )
                    
                    keyword_rankings.append({
                        'keyword_id': keyword.id,
                        'keyword': keyword.keyword,
                        'importance_score': float(importance_score),
                        'avg_tfidf_score': float(avg_metrics.avg_tfidf or 0),
                        'avg_engagement_score': float(avg_metrics.avg_engagement or 0),
                        'avg_sentiment_score': float(avg_metrics.avg_sentiment or 0),
                        'avg_virality_score': float(avg_metrics.avg_virality or 0),
                        'trend_velocity': float(avg_metrics.avg_velocity or 0),
                        'total_posts': int(avg_metrics.total_posts),
                        'last_updated': datetime.utcnow().isoformat()
                    })
            
            # Sort by importance score
            keyword_rankings.sort(key=lambda x: x['importance_score'], reverse=True)
            
            # Cache the results
            cache_key = f"keyword_ranking:user:{user_id}"
            await self.cache_manager.redis.set_json(cache_key, keyword_rankings, self.KEYWORD_RANKING_CACHE_TTL)
            
            return keyword_rankings
            
        except Exception as e:
            logger.error(f"Error getting keyword importance ranking: {str(e)}")
            return []
    
    def _create_empty_trend_data(self, keyword_id: int) -> Dict[str, Any]:
        """Create empty trend data structure for keywords with no posts."""
        return {
            "keyword_id": keyword_id,
            "avg_tfidf_score": 0.0,
            "avg_engagement_score": 0.0,
            "avg_sentiment_score": 0.0,
            "avg_virality_score": 0.0,
            "trend_velocity": 0.0,
            "total_posts": 0,
            "analyzed_at": datetime.utcnow().isoformat(),
            "cache_expires_at": (datetime.utcnow() + timedelta(seconds=self.TREND_DATA_CACHE_TTL)).isoformat(),
            "top_keywords": [],
            "engagement_distribution": {"low": 0, "medium": 0, "high": 0},
            "trend_direction": "neutral",
            "confidence_score": 0.0
        }
    
    def _calculate_sentiment_scores(self, posts: List[Post]) -> Dict[int, float]:
        """
        Calculate basic sentiment scores for posts.
        This is a simplified implementation - in production, you'd use a proper sentiment analysis library.
        """
        sentiment_scores = {}
        
        # Simple keyword-based sentiment analysis
        positive_words = ['good', 'great', 'excellent', 'amazing', 'awesome', 'love', 'best', 'perfect']
        negative_words = ['bad', 'terrible', 'awful', 'hate', 'worst', 'horrible', 'disgusting', 'stupid']
        
        for post in posts:
            text = f"{post.title} {post.content or ''}".lower()
            
            positive_count = sum(1 for word in positive_words if word in text)
            negative_count = sum(1 for word in negative_words if word in text)
            
            # Simple sentiment score calculation
            if positive_count + negative_count > 0:
                sentiment_score = (positive_count - negative_count) / (positive_count + negative_count)
            else:
                sentiment_score = 0.0
            
            sentiment_scores[post.id] = float(sentiment_score)
        
        return sentiment_scores
    
    def _calculate_virality_scores(self, posts: List[Post], db: Session) -> Dict[int, float]:
        """
        Calculate virality scores based on engagement growth rate.
        """
        virality_scores = {}
        
        for post in posts:
            # Simple virality calculation based on score per hour since creation
            if post.created_at:
                hours_since_creation = (datetime.utcnow() - post.created_at).total_seconds() / 3600
                if hours_since_creation > 0:
                    virality_score = post.score / hours_since_creation
                else:
                    virality_score = float(post.score)
            else:
                virality_score = 0.0
            
            # Normalize to 0-1 range
            virality_scores[post.id] = min(virality_score / 100.0, 1.0)
        
        return virality_scores
    
    def _extract_top_keywords(self, posts: List[Post], limit: int = 10) -> List[Dict[str, Any]]:
        """Extract top keywords from posts using TF-IDF."""
        try:
            if not posts:
                return []
            
            documents = [f"{post.title} {post.content or ''}" for post in posts]
            tfidf_matrix = self.tfidf_vectorizer.fit_transform(documents)
            feature_names = self.tfidf_vectorizer.get_feature_names_out()
            
            # Get average TF-IDF scores for each term
            mean_scores = np.mean(tfidf_matrix.toarray(), axis=0)
            
            # Create list of (term, score) pairs and sort by score
            term_scores = [(feature_names[i], float(mean_scores[i])) for i in range(len(feature_names))]
            term_scores.sort(key=lambda x: x[1], reverse=True)
            
            return [{"keyword": term, "score": score} for term, score in term_scores[:limit]]
        
        except Exception as e:
            logger.error(f"Error extracting top keywords: {str(e)}")
            return []
    
    def _calculate_engagement_distribution(self, engagement_scores: Dict[int, float]) -> Dict[str, int]:
        """Calculate distribution of engagement scores."""
        if not engagement_scores:
            return {"low": 0, "medium": 0, "high": 0}
        
        scores = list(engagement_scores.values())
        low_count = sum(1 for score in scores if score < 0.33)
        medium_count = sum(1 for score in scores if 0.33 <= score < 0.67)
        high_count = sum(1 for score in scores if score >= 0.67)
        
        return {"low": low_count, "medium": medium_count, "high": high_count}
    
    def _determine_trend_direction(self, trend_velocity: float) -> str:
        """Determine trend direction based on velocity."""
        if trend_velocity > 0.1:
            return "rising"
        elif trend_velocity < -0.1:
            return "falling"
        else:
            return "stable"
    
    def _calculate_confidence_score(self, post_count: int, trend_velocity: float) -> float:
        """Calculate confidence score for trend analysis."""
        # Base confidence on number of posts and trend velocity stability
        post_confidence = min(post_count / 50.0, 1.0)  # Max confidence at 50+ posts
        velocity_confidence = 1.0 - min(abs(trend_velocity), 1.0)  # Lower confidence for extreme velocities
        
        return float((post_confidence + velocity_confidence) / 2.0)
    
    async def _store_trend_history(self, keyword_id: int, trend_data: Dict[str, Any], db: Session):
        """Store trend data in history for tracking over time."""
        try:
            history_key = f"trend_history:keyword:{keyword_id}"
            
            # Get existing history
            existing_history = await self.cache_manager.redis.get_json(history_key) or []
            
            # Add current trend data to history
            history_entry = {
                "timestamp": datetime.utcnow().isoformat(),
                "avg_tfidf_score": trend_data["avg_tfidf_score"],
                "avg_engagement_score": trend_data["avg_engagement_score"],
                "trend_velocity": trend_data["trend_velocity"],
                "total_posts": trend_data["total_posts"],
                "confidence_score": trend_data["confidence_score"]
            }
            
            existing_history.append(history_entry)
            
            # Keep only last 30 entries (configurable)
            if len(existing_history) > 30:
                existing_history = existing_history[-30:]
            
            # Store updated history
            await self.cache_manager.redis.set_json(history_key, existing_history, self.TREND_HISTORY_CACHE_TTL)
            
        except Exception as e:
            logger.error(f"Error storing trend history for keyword_id {keyword_id}: {str(e)}")
    
    async def get_trend_history(self, keyword_id: int, days: int = 7) -> List[Dict[str, Any]]:
        """
        Get trend history for a keyword.
        
        Args:
            keyword_id: ID of the keyword
            days: Number of days of history to retrieve
            
        Returns:
            List of historical trend data points
        """
        try:
            history_key = f"trend_history:keyword:{keyword_id}"
            history = await self.cache_manager.redis.get_json(history_key) or []
            
            # Filter by date range
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            filtered_history = [
                entry for entry in history
                if datetime.fromisoformat(entry["timestamp"]) >= cutoff_date
            ]
            
            return filtered_history
            
        except Exception as e:
            logger.error(f"Error getting trend history for keyword_id {keyword_id}: {str(e)}")
            return []
    
    async def get_trend_summary(self, user_id: int, db: Session) -> Dict[str, Any]:
        """
        Get comprehensive trend summary for all user keywords.
        
        Args:
            user_id: ID of the user
            db: Database session
            
        Returns:
            Comprehensive trend summary
        """
        try:
            # Check cache first
            cache_key = f"trend_summary:user:{user_id}"
            cached_summary = await self.cache_manager.redis.get_json(cache_key)
            if cached_summary:
                return cached_summary
            
            # Get user keywords
            keywords = db.query(Keyword).filter(Keyword.user_id == user_id, Keyword.is_active == True).all()
            
            if not keywords:
                return {"user_id": user_id, "keywords": [], "summary": {}}
            
            keyword_summaries = []
            total_posts = 0
            total_engagement = 0.0
            total_tfidf = 0.0
            
            for keyword in keywords:
                # Get cached trend data for each keyword
                trend_data = await self.get_cached_trend_data(keyword.id)
                if trend_data:
                    keyword_summaries.append({
                        "keyword_id": keyword.id,
                        "keyword": keyword.keyword,
                        "trend_data": trend_data
                    })
                    total_posts += trend_data.get("total_posts", 0)
                    total_engagement += trend_data.get("avg_engagement_score", 0.0)
                    total_tfidf += trend_data.get("avg_tfidf_score", 0.0)
            
            # Calculate overall summary
            keyword_count = len(keyword_summaries)
            summary = {
                "total_keywords": keyword_count,
                "total_posts": total_posts,
                "avg_engagement_score": total_engagement / keyword_count if keyword_count > 0 else 0.0,
                "avg_tfidf_score": total_tfidf / keyword_count if keyword_count > 0 else 0.0,
                "generated_at": datetime.utcnow().isoformat()
            }
            
            result = {
                "user_id": user_id,
                "keywords": keyword_summaries,
                "summary": summary
            }
            
            # Cache the summary
            await self.cache_manager.redis.set_json(cache_key, result, self.TREND_SUMMARY_CACHE_TTL)
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting trend summary for user_id {user_id}: {str(e)}")
            return {"user_id": user_id, "keywords": [], "summary": {}, "error": str(e)}
    
    async def compare_keywords(self, keyword_ids: List[int], db: Session) -> Dict[str, Any]:
        """
        Compare trend data across multiple keywords.
        
        Args:
            keyword_ids: List of keyword IDs to compare
            db: Database session
            
        Returns:
            Comparison data for the keywords
        """
        try:
            comparison_data = []
            
            for keyword_id in keyword_ids:
                keyword = db.query(Keyword).filter(Keyword.id == keyword_id).first()
                if keyword:
                    trend_data = await self.get_cached_trend_data(keyword_id)
                    if trend_data:
                        comparison_data.append({
                            "keyword_id": keyword_id,
                            "keyword": keyword.keyword,
                            "trend_data": trend_data
                        })
            
            # Calculate comparison metrics
            if len(comparison_data) > 1:
                engagement_scores = [data["trend_data"]["avg_engagement_score"] for data in comparison_data]
                tfidf_scores = [data["trend_data"]["avg_tfidf_score"] for data in comparison_data]
                
                comparison_summary = {
                    "highest_engagement": max(engagement_scores),
                    "lowest_engagement": min(engagement_scores),
                    "avg_engagement": sum(engagement_scores) / len(engagement_scores),
                    "highest_tfidf": max(tfidf_scores),
                    "lowest_tfidf": min(tfidf_scores),
                    "avg_tfidf": sum(tfidf_scores) / len(tfidf_scores)
                }
            else:
                comparison_summary = {}
            
            return {
                "keywords": comparison_data,
                "comparison_summary": comparison_summary,
                "generated_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error comparing keywords {keyword_ids}: {str(e)}")
            return {"keywords": [], "comparison_summary": {}, "error": str(e)}


# Service instance
trend_analysis_service = TrendAnalysisService()