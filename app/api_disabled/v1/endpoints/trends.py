"""
Trend analysis API endpoints.
Enhanced with comprehensive caching and trend history tracking.
"""

import logging
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.keyword import Keyword
from app.services.trend_analysis_service import trend_analysis_service
from app.workers.analysis_tasks import (
    analyze_keyword_trends_task,
    analyze_all_user_keywords_task,
    calculate_keyword_importance_ranking_task
)
from app.schemas.trend import (
    TrendAnalysisResponse,
    KeywordRankingResponse,
    TrendAnalysisRequest,
    BulkAnalysisResponse,
    TrendSummaryResponse,
    TrendComparisonRequest,
    TrendComparisonResponse
)

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/analyze/{keyword_id}", response_model=Dict[str, Any])
async def start_trend_analysis(
    keyword_id: int,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Start trend analysis for a specific keyword.
    
    Args:
        keyword_id: ID of the keyword to analyze
        background_tasks: FastAPI background tasks
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Task information
    """
    try:
        # Verify keyword exists and belongs to user
        keyword = db.query(Keyword).filter(
            Keyword.id == keyword_id,
            Keyword.user_id == current_user.id
        ).first()
        
        if not keyword:
            raise HTTPException(
                status_code=404,
                detail=f"Keyword {keyword_id} not found or doesn't belong to user"
            )
        
        # Start analysis task
        task = analyze_keyword_trends_task.delay(keyword_id, current_user.id)
        
        logger.info(f"Started trend analysis task {task.id} for keyword_id: {keyword_id}")
        
        return {
            "message": "Trend analysis started",
            "task_id": task.id,
            "keyword_id": keyword_id,
            "keyword": keyword.keyword,
            "status": "started"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error starting trend analysis for keyword_id {keyword_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/analyze-all", response_model=Dict[str, Any])
async def start_bulk_trend_analysis(
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Start trend analysis for all user's keywords.
    
    Args:
        background_tasks: FastAPI background tasks
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Task information
    """
    try:
        # Check if user has any keywords
        keyword_count = db.query(Keyword).filter(
            Keyword.user_id == current_user.id,
            Keyword.is_active == True
        ).count()
        
        if keyword_count == 0:
            raise HTTPException(
                status_code=404,
                detail="No active keywords found for analysis"
            )
        
        # Start bulk analysis task
        task = analyze_all_user_keywords_task.delay(current_user.id)
        
        logger.info(f"Started bulk trend analysis task {task.id} for user_id: {current_user.id}")
        
        return {
            "message": "Bulk trend analysis started",
            "task_id": task.id,
            "user_id": current_user.id,
            "keyword_count": keyword_count,
            "status": "started"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error starting bulk trend analysis for user_id {current_user.id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/results/{keyword_id}", response_model=TrendAnalysisResponse)
async def get_trend_analysis_results(
    keyword_id: int,
    force_refresh: bool = Query(False, description="Force refresh of cached data"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get trend analysis results for a specific keyword.
    Enhanced with force refresh capability.
    
    Args:
        keyword_id: ID of the keyword
        force_refresh: Force refresh of cached data
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Trend analysis results
    """
    try:
        # Verify keyword exists and belongs to user
        keyword = db.query(Keyword).filter(
            Keyword.id == keyword_id,
            Keyword.user_id == current_user.id
        ).first()
        
        if not keyword:
            raise HTTPException(
                status_code=404,
                detail=f"Keyword {keyword_id} not found or doesn't belong to user"
            )
        
        # Get trend data (with optional force refresh)
        trend_data = await trend_analysis_service.analyze_keyword_trends(keyword_id, db, force_refresh)
        
        return TrendAnalysisResponse(
            keyword_id=keyword_id,
            keyword=keyword.keyword,
            trend_data=trend_data,
            cached=not force_refresh and "cache_expires_at" in trend_data
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting trend analysis results for keyword_id {keyword_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/rankings", response_model=KeywordRankingResponse)
async def get_keyword_rankings(
    force_refresh: bool = Query(False, description="Force refresh of cached rankings"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get keyword importance rankings for the current user.
    Enhanced with caching and force refresh capability.
    
    Args:
        force_refresh: Force refresh of cached rankings
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Keyword rankings
    """
    try:
        rankings = await trend_analysis_service.get_keyword_importance_ranking(current_user.id, db, force_refresh)
        
        return KeywordRankingResponse(
            user_id=current_user.id,
            rankings=rankings,
            total_keywords=len(rankings)
        )
        
    except Exception as e:
        logger.error(f"Error getting keyword rankings for user_id {current_user.id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/rankings/calculate", response_model=Dict[str, Any])
async def calculate_keyword_rankings(
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user)
):
    """
    Start calculation of keyword importance rankings.
    
    Args:
        background_tasks: FastAPI background tasks
        current_user: Current authenticated user
        
    Returns:
        Task information
    """
    try:
        # Start ranking calculation task
        task = calculate_keyword_importance_ranking_task.delay(current_user.id)
        
        logger.info(f"Started keyword ranking calculation task {task.id} for user_id: {current_user.id}")
        
        return {
            "message": "Keyword ranking calculation started",
            "task_id": task.id,
            "user_id": current_user.id,
            "status": "started"
        }
        
    except Exception as e:
        logger.error(f"Error starting keyword ranking calculation for user_id {current_user.id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/status/{task_id}")
async def get_analysis_task_status(
    task_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Get the status of a trend analysis task.
    
    Args:
        task_id: ID of the task
        current_user: Current authenticated user
        
    Returns:
        Task status information
    """
    try:
        from app.core.celery_app import celery_app
        
        # Get task result
        task_result = celery_app.AsyncResult(task_id)
        
        if task_result.state == 'PENDING':
            response = {
                'task_id': task_id,
                'state': task_result.state,
                'status': 'Task is waiting to be processed'
            }
        elif task_result.state == 'PROGRESS':
            response = {
                'task_id': task_id,
                'state': task_result.state,
                'current': task_result.info.get('current', 0),
                'total': task_result.info.get('total', 1),
                'status': task_result.info.get('status', '')
            }
        elif task_result.state == 'SUCCESS':
            response = {
                'task_id': task_id,
                'state': task_result.state,
                'result': task_result.result
            }
        else:  # FAILURE
            response = {
                'task_id': task_id,
                'state': task_result.state,
                'error': str(task_result.info)
            }
        
        return response
        
    except Exception as e:
        logger.error(f"Error getting task status for task_id {task_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.delete("/cache/{keyword_id}")
async def clear_trend_cache(
    keyword_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Clear cached trend data for a specific keyword.
    
    Args:
        keyword_id: ID of the keyword
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Success message
    """
    try:
        # Verify keyword exists and belongs to user
        keyword = db.query(Keyword).filter(
            Keyword.id == keyword_id,
            Keyword.user_id == current_user.id
        ).first()
        
        if not keyword:
            raise HTTPException(
                status_code=404,
                detail=f"Keyword {keyword_id} not found or doesn't belong to user"
            )
        
        # Clear cache using the service method
        success = await trend_analysis_service.invalidate_trend_cache(keyword_id)
        
        if success:
            logger.info(f"Cleared trend cache for keyword_id: {keyword_id}")
            return {
                "message": "Trend cache cleared successfully",
                "keyword_id": keyword_id,
                "keyword": keyword.keyword
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to clear cache")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error clearing trend cache for keyword_id {keyword_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/history/{keyword_id}")
async def get_trend_history(
    keyword_id: int,
    days: int = Query(7, ge=1, le=30, description="Number of days of history to retrieve"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get trend history for a specific keyword.
    
    Args:
        keyword_id: ID of the keyword
        days: Number of days of history to retrieve (1-30)
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Historical trend data
    """
    try:
        # Verify keyword exists and belongs to user
        keyword = db.query(Keyword).filter(
            Keyword.id == keyword_id,
            Keyword.user_id == current_user.id
        ).first()
        
        if not keyword:
            raise HTTPException(
                status_code=404,
                detail=f"Keyword {keyword_id} not found or doesn't belong to user"
            )
        
        # Get trend history
        history = await trend_analysis_service.get_trend_history(keyword_id, days)
        
        return {
            "keyword_id": keyword_id,
            "keyword": keyword.keyword,
            "days_requested": days,
            "history_count": len(history),
            "history": history
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting trend history for keyword_id {keyword_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/summary")
async def get_trend_summary(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get comprehensive trend summary for all user keywords.
    
    Args:
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Comprehensive trend summary
    """
    try:
        summary = await trend_analysis_service.get_trend_summary(current_user.id, db)
        return summary
        
    except Exception as e:
        logger.error(f"Error getting trend summary for user_id {current_user.id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/compare", response_model=TrendComparisonResponse)
async def compare_keyword_trends(
    request: TrendComparisonRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Compare trend data across multiple keywords.
    
    Args:
        request: Comparison request with keyword IDs
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Comparison data for the keywords
    """
    try:
        # Verify all keywords belong to the user
        keywords = db.query(Keyword).filter(
            Keyword.id.in_(request.keyword_ids),
            Keyword.user_id == current_user.id
        ).all()
        
        if len(keywords) != len(request.keyword_ids):
            raise HTTPException(
                status_code=404,
                detail="One or more keywords not found or don't belong to user"
            )
        
        # Get comparison data
        comparison_data = await trend_analysis_service.compare_keywords(request.keyword_ids, db)
        
        return TrendComparisonResponse(
            keywords=[kw.keyword for kw in keywords],
            comparison_data=comparison_data,
            time_range_days=request.time_range_days,
            generated_at=comparison_data.get("generated_at", "")
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error comparing keyword trends: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.delete("/cache/user")
async def clear_user_trend_cache(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Clear all cached trend data for the current user.
    
    Args:
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Success message with count of cleared items
    """
    try:
        # Get user's keywords
        keywords = db.query(Keyword).filter(Keyword.user_id == current_user.id).all()
        
        cleared_count = 0
        
        # Clear trend cache for each keyword
        for keyword in keywords:
            success = await trend_analysis_service.invalidate_trend_cache(keyword.id)
            if success:
                cleared_count += 1
        
        # Clear user-level caches
        from app.core.redis_client import cache_manager
        user_cache_keys = [
            f"keyword_ranking:user:{current_user.id}",
            f"trend_summary:user:{current_user.id}"
        ]
        
        for cache_key in user_cache_keys:
            await cache_manager.redis.delete(cache_key)
            cleared_count += 1
        
        logger.info(f"Cleared {cleared_count} cache entries for user_id: {current_user.id}")
        
        return {
            "message": "User trend cache cleared successfully",
            "user_id": current_user.id,
            "cleared_count": cleared_count,
            "keywords_processed": len(keywords)
        }
        
    except Exception as e:
        logger.error(f"Error clearing user trend cache for user_id {current_user.id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/cache/stats")
async def get_cache_statistics(
    current_user: User = Depends(get_current_user)
):
    """
    Get cache statistics for trend data.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        Cache statistics
    """
    try:
        from app.core.redis_client import cache_manager
        
        # Get general cache info
        cache_info = await cache_manager.get_cache_info()
        
        # Get trend-specific cache keys
        trend_keys = await cache_manager.redis.keys("trend:*")
        ranking_keys = await cache_manager.redis.keys("keyword_ranking:*")
        history_keys = await cache_manager.redis.keys("trend_history:*")
        summary_keys = await cache_manager.redis.keys("trend_summary:*")
        
        return {
            "cache_info": cache_info,
            "trend_cache_keys": len(trend_keys),
            "ranking_cache_keys": len(ranking_keys),
            "history_cache_keys": len(history_keys),
            "summary_cache_keys": len(summary_keys),
            "total_trend_related_keys": len(trend_keys) + len(ranking_keys) + len(history_keys) + len(summary_keys)
        }
        
    except Exception as e:
        logger.error(f"Error getting cache statistics: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")