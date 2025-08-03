"""
Posts API endpoints for retrieving and managing Reddit posts.
"""

from typing import Optional
from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user, get_db
from app.models.user import User
from app.services.post_service import PostService
from app.schemas.post import (
    PostListResponse, 
    PostDetailResponse, 
    PostQueryParams,
    PostResponse
)


router = APIRouter()


@router.get("/", response_model=PostListResponse)
async def get_posts(
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(10, ge=1, le=100, description="Items per page"),
    keyword_id: Optional[int] = Query(None, description="Filter by keyword ID"),
    subreddit: Optional[str] = Query(None, description="Filter by subreddit"),
    author: Optional[str] = Query(None, description="Filter by author"),
    search: Optional[str] = Query(None, description="Search in title and content"),
    sort_by: str = Query("created_at", description="Sort field (created_at, post_created_at, score, num_comments, title, author, subreddit)"),
    sort_order: str = Query("desc", pattern="^(asc|desc)$", description="Sort order"),
    min_score: Optional[int] = Query(None, description="Minimum score filter"),
    max_score: Optional[int] = Query(None, description="Maximum score filter"),
    date_from: Optional[str] = Query(None, description="Filter posts from this date (ISO format)"),
    date_to: Optional[str] = Query(None, description="Filter posts to this date (ISO format)"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get paginated list of posts with filtering and sorting options.
    Only returns posts from keywords owned by the authenticated user.
    
    **Filtering Options:**
    - keyword_id: Filter by specific keyword
    - subreddit: Filter by subreddit name (partial match)
    - author: Filter by author name (partial match)
    - search: Search in post title and content
    - min_score/max_score: Filter by score range
    - date_from/date_to: Filter by post creation date range
    
    **Sorting Options:**
    - sort_by: Field to sort by (created_at, post_created_at, score, num_comments, title, author, subreddit)
    - sort_order: asc or desc
    """
    try:
        # Parse date filters if provided
        date_from_parsed = None
        date_to_parsed = None
        
        if date_from:
            from datetime import datetime
            try:
                date_from_parsed = datetime.fromisoformat(date_from.replace('Z', '+00:00'))
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid date_from format. Use ISO format.")
        
        if date_to:
            from datetime import datetime
            try:
                date_to_parsed = datetime.fromisoformat(date_to.replace('Z', '+00:00'))
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid date_to format. Use ISO format.")

        # Create query parameters
        query_params = PostQueryParams(
            page=page,
            per_page=per_page,
            keyword_id=keyword_id,
            subreddit=subreddit,
            author=author,
            search=search,
            sort_by=sort_by,
            sort_order=sort_order,
            min_score=min_score,
            max_score=max_score,
            date_from=date_from_parsed,
            date_to=date_to_parsed
        )

        # Get posts using service
        post_service = PostService(db)
        result = await post_service.get_posts_paginated(current_user.id, query_params)
        
        return result

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve posts: {str(e)}")


@router.get("/{post_id}", response_model=PostDetailResponse)
async def get_post_detail(
    post_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get detailed information about a specific post, including comments.
    Only returns post if it belongs to a keyword owned by the authenticated user.
    """
    try:
        post_service = PostService(db)
        post = await post_service.get_post_by_id(post_id, current_user.id)
        
        if not post:
            raise HTTPException(status_code=404, detail="Post not found or access denied")
        
        return post

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve post: {str(e)}")


@router.get("/keyword/{keyword_id}", response_model=PostListResponse)
async def get_posts_by_keyword(
    keyword_id: int,
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(10, ge=1, le=100, description="Items per page"),
    sort_by: str = Query("created_at", description="Sort field"),
    sort_order: str = Query("desc", pattern="^(asc|desc)$", description="Sort order"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get posts for a specific keyword.
    Only returns posts if the keyword belongs to the authenticated user.
    """
    try:
        post_service = PostService(db)
        result = await post_service.get_posts_by_keyword(
            keyword_id=keyword_id,
            user_id=current_user.id,
            page=page,
            per_page=per_page,
            sort_by=sort_by,
            sort_order=sort_order
        )
        
        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve posts for keyword: {str(e)}")


@router.get("/search/query", response_model=PostListResponse)
async def search_posts(
    q: str = Query(..., description="Search query"),
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(10, ge=1, le=100, description="Items per page"),
    sort_by: str = Query("created_at", description="Sort field"),
    sort_order: str = Query("desc", pattern="^(asc|desc)$", description="Sort order"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Search posts by title and content.
    Only searches in posts from keywords owned by the authenticated user.
    """
    try:
        post_service = PostService(db)
        result = await post_service.search_posts(
            user_id=current_user.id,
            search_term=q,
            page=page,
            per_page=per_page,
            sort_by=sort_by,
            sort_order=sort_order
        )
        
        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to search posts: {str(e)}")


@router.get("/stats/summary")
async def get_post_statistics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get statistics about user's posts.
    Returns summary information like total posts, average score, etc.
    """
    try:
        post_service = PostService(db)
        stats = await post_service.get_post_statistics(current_user.id)
        
        return {
            "user_id": current_user.id,
            "statistics": stats
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve post statistics: {str(e)}")