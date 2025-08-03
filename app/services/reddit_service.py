"""
Reddit API client service for crawling posts and comments.
Implements rate limiting, retry logic, and data normalization.
"""

import asyncio
import logging
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from dataclasses import dataclass
import time

import praw
from praw.exceptions import RedditAPIException
from prawcore.exceptions import PrawcoreException
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
import httpx

from app.core.config import settings
from app.core.metrics import (
    record_reddit_api_call, update_reddit_api_rate_limit,
    record_error, record_posts_crawled
)
from app.core.logging import get_logger, ErrorCategory


logger = get_logger(__name__)


@dataclass
class RedditPostData:
    """Normalized Reddit post data structure."""
    reddit_id: str
    title: str
    content: str
    author: str
    score: int
    num_comments: int
    url: str
    subreddit: str
    created_at: datetime


@dataclass
class RedditCommentData:
    """Normalized Reddit comment data structure."""
    reddit_id: str
    body: str
    author: str
    score: int
    created_at: datetime


class RateLimiter:
    """Simple rate limiter for Reddit API calls."""
    
    def __init__(self, requests_per_minute: int = 60, requests_per_second: int = 1):
        self.requests_per_minute = requests_per_minute
        self.requests_per_second = requests_per_second
        self.minute_requests = []
        self.last_request_time = 0
    
    async def wait_if_needed(self):
        """Wait if rate limit would be exceeded."""
        current_time = time.time()
        
        # Remove requests older than 1 minute
        self.minute_requests = [
            req_time for req_time in self.minute_requests 
            if current_time - req_time < 60
        ]
        
        # Check per-minute limit
        if len(self.minute_requests) >= self.requests_per_minute:
            wait_time = 60 - (current_time - self.minute_requests[0])
            if wait_time > 0:
                logger.info(
                "Rate limit reached, waiting for cooldown",
                operation="reddit_rate_limit",
                wait_time=wait_time,
                requests_in_minute=len(self.minute_requests)
            )
                await asyncio.sleep(wait_time)
        
        # Check per-second limit
        if current_time - self.last_request_time < 1.0:
            wait_time = 1.0 - (current_time - self.last_request_time)
            await asyncio.sleep(wait_time)
        
        # Record this request
        self.minute_requests.append(time.time())
        self.last_request_time = time.time()


class RedditAPIClient:
    """Reddit API client with authentication, rate limiting, and error handling."""
    
    def __init__(self):
        self.reddit = None
        self.rate_limiter = RateLimiter(
            requests_per_minute=settings.REDDIT_REQUESTS_PER_MINUTE,
            requests_per_second=settings.REDDIT_REQUESTS_PER_SECOND
        )
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize the PRAW Reddit client."""
        try:
            self.reddit = praw.Reddit(
                client_id=settings.REDDIT_CLIENT_ID,
                client_secret=settings.REDDIT_CLIENT_SECRET,
                user_agent=settings.REDDIT_USER_AGENT,
                # Using read-only mode for public data
                username=None,
                password=None
            )
            
            # Test the connection
            self.reddit.user.me()
            logger.info("Reddit API client initialized successfully")
            
        except Exception as e:
            logger.error(
                "Failed to initialize Reddit API client",
                error_category=ErrorCategory.EXTERNAL_API,
                alert_level="high",
                operation="reddit_client_init",
                error=str(e),
                exc_info=True
            )
            # Initialize with read-only access for public data
            self.reddit = praw.Reddit(
                client_id=settings.REDDIT_CLIENT_ID,
                client_secret=settings.REDDIT_CLIENT_SECRET,
                user_agent=settings.REDDIT_USER_AGENT
            )
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type((RedditAPIException, PrawcoreException, httpx.RequestError))
    )
    async def search_posts_by_keyword(
        self, 
        keyword: str, 
        limit: int = 100,
        time_filter: str = "week",
        sort: str = "hot"
    ) -> List[RedditPostData]:
        """
        Search Reddit posts by keyword with rate limiting and retry logic.
        
        Args:
            keyword: Search keyword
            limit: Maximum number of posts to retrieve
            time_filter: Time filter (hour, day, week, month, year, all)
            sort: Sort method (relevance, hot, top, new, comments)
        
        Returns:
            List of normalized Reddit post data
        """
        await self.rate_limiter.wait_if_needed()
        
        start_time = time.time()
        
        try:
            logger.info(
                "Starting Reddit post search",
                operation="reddit_search_posts",
                keyword=keyword,
                limit=limit
            )
            
            posts_data = []
            
            # Search across all subreddits
            search_results = self.reddit.subreddit("all").search(
                keyword,
                sort=sort,
                time_filter=time_filter,
                limit=limit
            )
            
            # Record successful API call
            response_time = time.time() - start_time
            record_reddit_api_call("search", "success", response_time)
            
            for submission in search_results:
                try:
                    post_data = self._normalize_post_data(submission)
                    posts_data.append(post_data)
                    
                    # Record posts crawled metric
                    record_posts_crawled(keyword, post_data.subreddit, 1)
                    
                    # Add small delay between processing posts
                    await asyncio.sleep(0.1)
                    
                except Exception as e:
                    logger.warning(f"Failed to process post {submission.id}: {e}")
                    record_error(type(e).__name__, 'reddit_post_processing')
                    continue
            
            logger.info(f"Successfully retrieved {len(posts_data)} posts for keyword '{keyword}'")
            return posts_data
            
        except Exception as e:
            # Record failed API call
            response_time = time.time() - start_time
            record_reddit_api_call("search", "failure", response_time)
            record_error(type(e).__name__, 'reddit_search')
            logger.error(
                "Failed to search Reddit posts",
                error_category=ErrorCategory.EXTERNAL_API,
                alert_level="medium",
                operation="reddit_search_posts",
                keyword=keyword,
                error=str(e),
                exc_info=True
            )
            raise
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type((RedditAPIException, PrawcoreException, httpx.RequestError))
    )
    async def get_post_comments(
        self, 
        post_reddit_id: str, 
        limit: int = 50
    ) -> List[RedditCommentData]:
        """
        Get comments for a specific Reddit post.
        
        Args:
            post_reddit_id: Reddit post ID
            limit: Maximum number of comments to retrieve
        
        Returns:
            List of normalized Reddit comment data
        """
        await self.rate_limiter.wait_if_needed()
        
        try:
            logger.info(f"Fetching comments for post: {post_reddit_id} (limit: {limit})")
            
            submission = self.reddit.submission(id=post_reddit_id)
            
            # Expand comment tree and limit comments
            submission.comments.replace_more(limit=0)
            comments_data = []
            
            # Get top-level comments up to limit
            for comment in submission.comments[:limit]:
                try:
                    if hasattr(comment, 'body') and comment.body != '[deleted]':
                        comment_data = self._normalize_comment_data(comment)
                        comments_data.append(comment_data)
                        
                        # Add small delay between processing comments
                        await asyncio.sleep(0.05)
                        
                except Exception as e:
                    logger.warning(f"Failed to process comment {comment.id}: {e}")
                    continue
            
            logger.info(f"Successfully retrieved {len(comments_data)} comments for post {post_reddit_id}")
            return comments_data
            
        except Exception as e:
            logger.error(f"Failed to get comments for post {post_reddit_id}: {e}")
            raise
    
    def _normalize_post_data(self, submission) -> RedditPostData:
        """
        Normalize Reddit submission data to our internal format.
        
        Args:
            submission: PRAW submission object
        
        Returns:
            Normalized RedditPostData
        """
        # Handle selftext vs url content
        content = ""
        if hasattr(submission, 'selftext') and submission.selftext:
            content = submission.selftext
        elif hasattr(submission, 'url') and submission.url:
            content = f"Link: {submission.url}"
        
        # Convert Unix timestamp to datetime
        created_at = datetime.fromtimestamp(submission.created_utc, tz=timezone.utc)
        
        return RedditPostData(
            reddit_id=submission.id,
            title=submission.title or "",
            content=content,
            author=str(submission.author) if submission.author else "[deleted]",
            score=submission.score or 0,
            num_comments=submission.num_comments or 0,
            url=submission.url or "",
            subreddit=str(submission.subreddit),
            created_at=created_at
        )
    
    def _normalize_comment_data(self, comment) -> RedditCommentData:
        """
        Normalize Reddit comment data to our internal format.
        
        Args:
            comment: PRAW comment object
        
        Returns:
            Normalized RedditCommentData
        """
        # Convert Unix timestamp to datetime
        created_at = datetime.fromtimestamp(comment.created_utc, tz=timezone.utc)
        
        return RedditCommentData(
            reddit_id=comment.id,
            body=comment.body or "",
            author=str(comment.author) if comment.author else "[deleted]",
            score=comment.score or 0,
            created_at=created_at
        )
    
    async def get_subreddit_posts(
        self,
        subreddit_name: str,
        limit: int = 100,
        sort: str = "hot"
    ) -> List[RedditPostData]:
        """
        Get posts from a specific subreddit.
        
        Args:
            subreddit_name: Name of the subreddit
            limit: Maximum number of posts to retrieve
            sort: Sort method (hot, new, top, rising)
        
        Returns:
            List of normalized Reddit post data
        """
        await self.rate_limiter.wait_if_needed()
        
        try:
            logger.info(f"Fetching posts from r/{subreddit_name} (limit: {limit}, sort: {sort})")
            
            subreddit = self.reddit.subreddit(subreddit_name)
            posts_data = []
            
            # Get posts based on sort method
            if sort == "hot":
                submissions = subreddit.hot(limit=limit)
            elif sort == "new":
                submissions = subreddit.new(limit=limit)
            elif sort == "top":
                submissions = subreddit.top(limit=limit)
            elif sort == "rising":
                submissions = subreddit.rising(limit=limit)
            else:
                submissions = subreddit.hot(limit=limit)
            
            for submission in submissions:
                try:
                    post_data = self._normalize_post_data(submission)
                    posts_data.append(post_data)
                    
                    # Add small delay between processing posts
                    await asyncio.sleep(0.1)
                    
                except Exception as e:
                    logger.warning(f"Failed to process post {submission.id}: {e}")
                    continue
            
            logger.info(f"Successfully retrieved {len(posts_data)} posts from r/{subreddit_name}")
            return posts_data
            
        except Exception as e:
            logger.error(f"Failed to get posts from r/{subreddit_name}: {e}")
            raise
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Check Reddit API connection health.
        
        Returns:
            Health status information
        """
        try:
            await self.rate_limiter.wait_if_needed()
            
            # Try to access Reddit API
            test_subreddit = self.reddit.subreddit("test")
            test_subreddit.display_name  # This will trigger an API call
            
            return {
                "status": "healthy",
                "message": "Reddit API connection is working",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "message": f"Reddit API connection failed: {str(e)}",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }


# Global Reddit client instance
reddit_client = RedditAPIClient()