"""
API endpoints for Reddit crawling operations.
Provides functionality to start, monitor, and manage crawling tasks.
"""

import logging
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Path
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.services.task_service import TaskService
from app.services.keyword_service import KeywordService
from app.workers.crawling_tasks import (
    crawl_keyword_posts,
    crawl_all_active_keywords,
    crawl_subreddit_posts
)

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/keyword/{keyword_id}")
async def start_keyword_crawl(
    keyword_id: int = Path(..., description="ID of the keyword to crawl posts for"),
    limit: int = Query(100, ge=1, le=500, description="Maximum number of posts to crawl"),
    time_filter: str = Query("week", regex="^(hour|day|week|month|year|all)$", description="Time filter for posts"),
    sort: str = Query("hot", regex="^(relevance|hot|top|new|comments)$", description="Sort method for posts"),
    include_comments: bool = Query(True, description="Whether to fetch comments for each post"),
    comment_limit: int = Query(20, ge=0, le=100, description="Maximum number of comments per post"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Start crawling Reddit posts for a specific keyword.
    
    Args:
        keyword_id: ID of the keyword to crawl posts for
        limit: Maximum number of posts to crawl
        time_filter: Time filter for posts (hour, day, week, month, year, all)
        sort: Sort method (relevance, hot, top, new, comments)
        include_comments: Whether to fetch comments for each post
        comment_limit: Maximum number of comments per post
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Crawl task start result
    """
    try:
        # Verify keyword belongs to user
        keyword_service = KeywordService(db)
        keyword = await keyword_service.get_keyword_by_id(keyword_id, current_user.id)
        
        if not keyword:
            raise HTTPException(
                status_code=404, 
                detail=f"Keyword with ID {keyword_id} not found or does not belong to user"
            )
        
        if not keyword.is_active:
            raise HTTPException(
                status_code=400,
                detail=f"Keyword '{keyword.keyword}' is not active"
            )
        
        # Start the crawl task
        task_result = crawl_keyword_posts.delay(
            keyword_id=keyword_id,
            limit=limit,
            time_filter=time_filter,
            sort=sort,
            include_comments=include_comments,
            comment_limit=comment_limit
        )
        
        # Log the task start
        task_service = TaskService(db)
        process_log = task_service.log_task_start(
            user_id=current_user.id,
            task_type="crawling",
            task_id=task_result.id
        )
        
        return {
            "success": True,
            "data": {
                "task_id": task_result.id,
                "status": "started",
                "message": f"Crawl started for keyword '{keyword.keyword}'",
                "keyword_id": keyword_id,
                "keyword": keyword.keyword,
                "limit": limit,
                "time_filter": time_filter,
                "sort": sort,
                "include_comments": include_comments,
                "comment_limit": comment_limit,
                "process_log_id": process_log.id
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error starting keyword crawl: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to start keyword crawl: {str(e)}")


@router.post("/all-keywords")
async def start_all_keywords_crawl(
    limit_per_keyword: int = Query(50, ge=1, le=200, description="Maximum number of posts per keyword"),
    time_filter: str = Query("day", regex="^(hour|day|week|month|year|all)$", description="Time filter for posts"),
    sort: str = Query("hot", regex="^(relevance|hot|top|new|comments)$", description="Sort method for posts"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Start crawling Reddit posts for all active keywords of the current user.
    
    Args:
        limit_per_keyword: Maximum number of posts per keyword
        time_filter: Time filter for posts (hour, day, week, month, year, all)
        sort: Sort method (relevance, hot, top, new, comments)
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Crawl task start result
    """
    try:
        # Start the crawl task for user's keywords
        task_result = crawl_all_active_keywords.delay(
            user_id=current_user.id,
            limit_per_keyword=limit_per_keyword,
            time_filter=time_filter,
            sort=sort
        )
        
        # Log the task start
        task_service = TaskService(db)
        process_log = task_service.log_task_start(
            user_id=current_user.id,
            task_type="crawling",
            task_id=task_result.id
        )
        
        return {
            "success": True,
            "data": {
                "task_id": task_result.id,
                "status": "started",
                "message": "Crawl started for all active keywords",
                "user_id": current_user.id,
                "limit_per_keyword": limit_per_keyword,
                "time_filter": time_filter,
                "sort": sort,
                "process_log_id": process_log.id
            }
        }
        
    except Exception as e:
        logger.error(f"Error starting all keywords crawl: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to start all keywords crawl: {str(e)}")


@router.post("/subreddit")
async def start_subreddit_crawl(
    subreddit_name: str = Query(..., min_length=1, max_length=50, description="Name of the subreddit to crawl"),
    keyword_id: int = Query(..., description="ID of the keyword to associate posts with"),
    limit: int = Query(100, ge=1, le=500, description="Maximum number of posts to crawl"),
    sort: str = Query("hot", regex="^(hot|new|top|rising)$", description="Sort method for posts"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Start crawling Reddit posts from a specific subreddit.
    
    Args:
        subreddit_name: Name of the subreddit to crawl
        keyword_id: ID of the keyword to associate posts with
        limit: Maximum number of posts to crawl
        sort: Sort method (hot, new, top, rising)
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Crawl task start result
    """
    try:
        # Verify keyword belongs to user
        keyword_service = KeywordService(db)
        keyword = await keyword_service.get_keyword_by_id(keyword_id, current_user.id)
        
        if not keyword:
            raise HTTPException(
                status_code=404,
                detail=f"Keyword with ID {keyword_id} not found or does not belong to user"
            )
        
        # Clean subreddit name (remove r/ prefix if present)
        clean_subreddit_name = subreddit_name.lower().strip()
        if clean_subreddit_name.startswith('r/'):
            clean_subreddit_name = clean_subreddit_name[2:]
        
        # Start the crawl task
        task_result = crawl_subreddit_posts.delay(
            subreddit_name=clean_subreddit_name,
            keyword_id=keyword_id,
            limit=limit,
            sort=sort
        )
        
        # Log the task start
        task_service = TaskService(db)
        process_log = task_service.log_task_start(
            user_id=current_user.id,
            task_type="crawling",
            task_id=task_result.id
        )
        
        return {
            "success": True,
            "data": {
                "task_id": task_result.id,
                "status": "started",
                "message": f"Crawl started for r/{clean_subreddit_name}",
                "subreddit": clean_subreddit_name,
                "keyword_id": keyword_id,
                "keyword": keyword.keyword,
                "limit": limit,
                "sort": sort,
                "process_log_id": process_log.id
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error starting subreddit crawl: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to start subreddit crawl: {str(e)}")


@router.get("/status")
async def get_crawl_status(
    limit: int = Query(20, ge=1, le=100, description="Maximum number of tasks to return"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get the status of all crawling tasks for the current user.
    
    Args:
        limit: Maximum number of tasks to return
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Crawling tasks status
    """
    try:
        task_service = TaskService(db)
        
        # Get crawling tasks for the user
        crawling_tasks = task_service.get_user_tasks(
            user_id=current_user.id,
            task_type="crawling",
            limit=limit
        )
        
        # Get detailed status for each task
        task_statuses = []
        for task in crawling_tasks:
            status_info = task_service.get_task_status(task.task_id)
            
            task_info = {
                "id": task.id,
                "task_id": task.task_id,
                "status": task.status,
                "created_at": task.created_at.isoformat() if task.created_at else None,
                "completed_at": task.completed_at.isoformat() if task.completed_at else None,
                "error_message": task.error_message,
                "celery_status": status_info.get("status"),
                "progress": status_info.get("progress"),
                "result": status_info.get("result")
            }
            
            # Parse task metadata if available
            if task.task_metadata:
                try:
                    import json
                    task_info["metadata"] = json.loads(task.task_metadata)
                except:
                    pass
            
            task_statuses.append(task_info)
        
        return {
            "success": True,
            "data": {
                "tasks": task_statuses,
                "total": len(task_statuses)
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting crawl status: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get crawl status: {str(e)}")


@router.get("/statistics")
async def get_crawl_statistics(
    days: int = Query(7, ge=1, le=365, description="Number of days to include in statistics"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get crawling statistics for the current user.
    
    Args:
        days: Number of days to include in statistics
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Crawling statistics
    """
    try:
        task_service = TaskService(db)
        
        # Get task statistics for crawling tasks
        stats = task_service.get_task_statistics(
            user_id=current_user.id,
            days=days
        )
        
        # Filter for crawling tasks only
        crawling_stats = stats.get("by_type", {}).get("crawling", {
            "total": 0,
            "completed": 0,
            "failed": 0,
            "running": 0,
            "pending": 0,
            "cancelled": 0
        })
        
        # Calculate success rate for crawling tasks
        if crawling_stats["total"] > 0:
            crawling_stats["success_rate"] = (crawling_stats["completed"] / crawling_stats["total"]) * 100
        else:
            crawling_stats["success_rate"] = 0
        
        return {
            "success": True,
            "data": {
                "period_days": days,
                "crawling_tasks": crawling_stats,
                "overall_stats": stats
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting crawl statistics: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get crawl statistics: {str(e)}")


@router.delete("/task/{task_id}")
async def cancel_crawl_task(
    task_id: str = Path(..., description="ID of the task to cancel"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Cancel a running crawling task.
    
    Args:
        task_id: ID of the task to cancel
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Cancellation result
    """
    try:
        task_service = TaskService(db)
        
        # Verify task belongs to user
        user_tasks = task_service.get_user_tasks(
            user_id=current_user.id,
            task_type="crawling",
            limit=1000  # Get all tasks to find the specific one
        )
        
        task_found = any(task.task_id == task_id for task in user_tasks)
        if not task_found:
            raise HTTPException(
                status_code=404,
                detail="Task not found or does not belong to user"
            )
        
        # Cancel the task
        result = task_service.cancel_task(task_id)
        
        return {
            "success": True,
            "data": result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error cancelling crawl task: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to cancel crawl task: {str(e)}")