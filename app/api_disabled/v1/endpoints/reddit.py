"""
Reddit API endpoints for testing the Reddit service.
"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel

from app.services.reddit_service import reddit_client, RedditPostData, RedditCommentData
from app.core.dependencies import get_current_user
from app.models.user import User


router = APIRouter()


class RedditPostResponse(BaseModel):
    """Response model for Reddit posts."""
    reddit_id: str
    title: str
    content: str
    author: str
    score: int
    num_comments: int
    url: str
    subreddit: str
    created_at: str


class RedditCommentResponse(BaseModel):
    """Response model for Reddit comments."""
    reddit_id: str
    body: str
    author: str
    score: int
    created_at: str


class RedditHealthResponse(BaseModel):
    """Response model for Reddit API health check."""
    status: str
    message: str
    timestamp: str


@router.get("/health", response_model=RedditHealthResponse)
async def reddit_health_check():
    """
    Check Reddit API connection health.
    """
    try:
        health_status = await reddit_client.health_check()
        return RedditHealthResponse(**health_status)
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Reddit API health check failed: {str(e)}")


@router.get("/search", response_model=List[RedditPostResponse])
async def search_reddit_posts(
    keyword: str = Query(..., description="Keyword to search for"),
    limit: int = Query(10, ge=1, le=100, description="Number of posts to retrieve"),
    time_filter: str = Query("week", description="Time filter (hour, day, week, month, year, all)"),
    sort: str = Query("hot", description="Sort method (relevance, hot, top, new, comments)"),
    current_user: User = Depends(get_current_user)
):
    """
    Search Reddit posts by keyword.
    Requires authentication.
    """
    try:
        posts_data = await reddit_client.search_posts_by_keyword(
            keyword=keyword,
            limit=limit,
            time_filter=time_filter,
            sort=sort
        )
        
        # Convert to response format
        posts_response = []
        for post in posts_data:
            posts_response.append(RedditPostResponse(
                reddit_id=post.reddit_id,
                title=post.title,
                content=post.content,
                author=post.author,
                score=post.score,
                num_comments=post.num_comments,
                url=post.url,
                subreddit=post.subreddit,
                created_at=post.created_at.isoformat()
            ))
        
        return posts_response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to search Reddit posts: {str(e)}")


@router.get("/posts/{post_id}/comments", response_model=List[RedditCommentResponse])
async def get_reddit_post_comments(
    post_id: str,
    limit: int = Query(20, ge=1, le=100, description="Number of comments to retrieve"),
    current_user: User = Depends(get_current_user)
):
    """
    Get comments for a specific Reddit post.
    Requires authentication.
    """
    try:
        comments_data = await reddit_client.get_post_comments(
            post_reddit_id=post_id,
            limit=limit
        )
        
        # Convert to response format
        comments_response = []
        for comment in comments_data:
            comments_response.append(RedditCommentResponse(
                reddit_id=comment.reddit_id,
                body=comment.body,
                author=comment.author,
                score=comment.score,
                created_at=comment.created_at.isoformat()
            ))
        
        return comments_response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get Reddit post comments: {str(e)}")


@router.get("/subreddit/{subreddit_name}", response_model=List[RedditPostResponse])
async def get_subreddit_posts(
    subreddit_name: str,
    limit: int = Query(10, ge=1, le=100, description="Number of posts to retrieve"),
    sort: str = Query("hot", description="Sort method (hot, new, top, rising)"),
    current_user: User = Depends(get_current_user)
):
    """
    Get posts from a specific subreddit.
    Requires authentication.
    """
    try:
        posts_data = await reddit_client.get_subreddit_posts(
            subreddit_name=subreddit_name,
            limit=limit,
            sort=sort
        )
        
        # Convert to response format
        posts_response = []
        for post in posts_data:
            posts_response.append(RedditPostResponse(
                reddit_id=post.reddit_id,
                title=post.title,
                content=post.content,
                author=post.author,
                score=post.score,
                num_comments=post.num_comments,
                url=post.url,
                subreddit=post.subreddit,
                created_at=post.created_at.isoformat()
            ))
        
        return posts_response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get subreddit posts: {str(e)}")