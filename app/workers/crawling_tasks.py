"""
Celery tasks for Reddit content crawling.
Implements background tasks for crawling Reddit posts and comments.
"""

import asyncio
import logging
import json
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.core.celery_app import celery_app, BaseTask
from app.core.database import get_db
from app.core.celery_metrics import business_metrics_task
from app.models.keyword import Keyword
from app.models.post import Post, Comment
from app.models.process_log import ProcessLog
from app.services.reddit_service import reddit_client, RedditPostData, RedditCommentData

logger = logging.getLogger(__name__)


def get_db_session() -> Session:
    """Get database session for Celery tasks."""
    return next(get_db())


@celery_app.task(bind=True, base=BaseTask, name="crawl_keyword_posts")
@business_metrics_task
def crawl_keyword_posts(
    self, 
    keyword_id: int, 
    limit: int = 100,
    time_filter: str = "week",
    sort: str = "hot",
    include_comments: bool = True,
    comment_limit: int = 20
) -> Dict[str, Any]:
    """
    Crawl Reddit posts for a specific keyword and store in database.
    
    Args:
        keyword_id: ID of the keyword to crawl posts for
        limit: Maximum number of posts to retrieve
        time_filter: Time filter (hour, day, week, month, year, all)
        sort: Sort method (relevance, hot, top, new, comments)
        include_comments: Whether to fetch comments for each post
        comment_limit: Maximum number of comments per post
        
    Returns:
        Dictionary containing task result
    """
    db = None
    try:
        # Get database session
        db = get_db_session()
        
        # Update task progress
        self.update_state(
            state='PROGRESS',
            meta={'current': 0, 'total': 100, 'status': f'Starting crawl for keyword {keyword_id}...'}
        )
        
        logger.info(f"Task {self.name} [{self.request.id}] started for keyword {keyword_id}")
        
        # Get keyword from database
        keyword = db.query(Keyword).filter(Keyword.id == keyword_id).first()
        if not keyword:
            raise ValueError(f"Keyword with ID {keyword_id} not found")
        
        if not keyword.is_active:
            logger.warning(f"Keyword {keyword_id} is not active, skipping crawl")
            return {
                "status": "skipped",
                "message": f"Keyword '{keyword.keyword}' is not active",
                "keyword_id": keyword_id,
                "task_id": self.request.id
            }
        
        # Update process log to running
        process_log = db.query(ProcessLog).filter(
            ProcessLog.task_id == self.request.id
        ).first()
        if process_log:
            process_log.status = "running"
            process_log.total_items = limit
            db.commit()
        
        # Update progress
        self.update_state(
            state='PROGRESS',
            meta={'current': 10, 'total': 100, 'status': f'Fetching posts for keyword: {keyword.keyword}'}
        )
        
        # Fetch posts from Reddit
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            posts_data = loop.run_until_complete(
                reddit_client.search_posts_by_keyword(
                    keyword=keyword.keyword,
                    limit=limit,
                    time_filter=time_filter,
                    sort=sort
                )
            )
        finally:
            loop.close()
        
        if not posts_data:
            logger.warning(f"No posts found for keyword '{keyword.keyword}'")
            return {
                "status": "completed",
                "message": f"No posts found for keyword '{keyword.keyword}'",
                "keyword_id": keyword_id,
                "posts_saved": 0,
                "comments_saved": 0,
                "task_id": self.request.id
            }
        
        # Update progress
        self.update_state(
            state='PROGRESS',
            meta={'current': 30, 'total': 100, 'status': f'Found {len(posts_data)} posts, saving to database...'}
        )
        
        # Save posts to database
        posts_saved = 0
        comments_saved = 0
        
        for i, post_data in enumerate(posts_data):
            try:
                # Check if post already exists
                existing_post = db.query(Post).filter(
                    Post.reddit_id == post_data.reddit_id
                ).first()
                
                if existing_post:
                    logger.debug(f"Post {post_data.reddit_id} already exists, skipping")
                    continue
                
                # Create new post
                db_post = Post(
                    keyword_id=keyword_id,
                    reddit_id=post_data.reddit_id,
                    title=post_data.title,
                    content=post_data.content,
                    author=post_data.author,
                    score=post_data.score,
                    num_comments=post_data.num_comments,
                    url=post_data.url,
                    subreddit=post_data.subreddit,
                    post_created_at=post_data.created_at
                )
                
                db.add(db_post)
                db.commit()
                db.refresh(db_post)
                posts_saved += 1
                
                # Update progress
                progress = 30 + (i / len(posts_data)) * 40  # 30-70% for posts
                self.update_state(
                    state='PROGRESS',
                    meta={
                        'current': int(progress), 
                        'total': 100, 
                        'status': f'Saved post {i+1}/{len(posts_data)}: {post_data.title[:50]}...'
                    }
                )
                
                # Fetch comments if requested
                if include_comments and post_data.num_comments > 0:
                    try:
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)
                        
                        try:
                            comments_data = loop.run_until_complete(
                                reddit_client.get_post_comments(
                                    post_reddit_id=post_data.reddit_id,
                                    limit=comment_limit
                                )
                            )
                        finally:
                            loop.close()
                        
                        # Save comments
                        for comment_data in comments_data:
                            try:
                                # Check if comment already exists
                                existing_comment = db.query(Comment).filter(
                                    Comment.reddit_id == comment_data.reddit_id
                                ).first()
                                
                                if existing_comment:
                                    continue
                                
                                db_comment = Comment(
                                    post_id=db_post.id,
                                    reddit_id=comment_data.reddit_id,
                                    body=comment_data.body,
                                    author=comment_data.author,
                                    score=comment_data.score,
                                    comment_created_at=comment_data.created_at
                                )
                                
                                db.add(db_comment)
                                comments_saved += 1
                                
                            except IntegrityError:
                                db.rollback()
                                logger.debug(f"Comment {comment_data.reddit_id} already exists")
                                continue
                        
                        db.commit()
                        
                    except Exception as e:
                        logger.warning(f"Failed to fetch comments for post {post_data.reddit_id}: {e}")
                        continue
                
            except IntegrityError:
                db.rollback()
                logger.debug(f"Post {post_data.reddit_id} already exists")
                continue
            except Exception as e:
                logger.error(f"Failed to save post {post_data.reddit_id}: {e}")
                db.rollback()
                continue
        
        # Update progress
        self.update_state(
            state='PROGRESS',
            meta={'current': 90, 'total': 100, 'status': 'Finalizing crawl results...'}
        )
        
        # Update process log
        if process_log:
            process_log.status = "completed"
            process_log.completed_at = datetime.utcnow()
            process_log.items_processed = posts_saved
            process_log.task_metadata = json.dumps({
                "keyword": keyword.keyword,
                "posts_found": len(posts_data),
                "posts_saved": posts_saved,
                "comments_saved": comments_saved,
                "time_filter": time_filter,
                "sort": sort
            })
            db.commit()
        
        result = {
            "status": "completed",
            "message": f"Successfully crawled posts for keyword '{keyword.keyword}'",
            "keyword_id": keyword_id,
            "keyword": keyword.keyword,
            "posts_found": len(posts_data),
            "posts_saved": posts_saved,
            "comments_saved": comments_saved,
            "task_id": self.request.id
        }
        
        logger.info(f"Task {self.name} [{self.request.id}] completed for keyword {keyword_id}: {posts_saved} posts, {comments_saved} comments")
        return result
        
    except Exception as exc:
        logger.error(f"Task {self.name} [{self.request.id}] failed for keyword {keyword_id}: {exc}")
        
        # Update process log with error
        if db:
            try:
                process_log = db.query(ProcessLog).filter(
                    ProcessLog.task_id == self.request.id
                ).first()
                if process_log:
                    process_log.status = "failed"
                    process_log.completed_at = datetime.utcnow()
                    process_log.error_message = str(exc)
                    db.commit()
            except Exception as e:
                logger.error(f"Failed to update process log: {e}")
        
        raise
    finally:
        if db:
            db.close()


@celery_app.task(bind=True, base=BaseTask, name="crawl_all_active_keywords")
def crawl_all_active_keywords(
    self,
    user_id: Optional[int] = None,
    limit_per_keyword: int = 50,
    time_filter: str = "day",
    sort: str = "hot"
) -> Dict[str, Any]:
    """
    Crawl posts for all active keywords (optionally for a specific user).
    
    Args:
        user_id: Optional user ID to crawl keywords for (if None, crawls all users)
        limit_per_keyword: Maximum number of posts per keyword
        time_filter: Time filter for posts
        sort: Sort method for posts
        
    Returns:
        Dictionary containing task result
    """
    db = None
    try:
        # Get database session
        db = get_db_session()
        
        # Update task progress
        self.update_state(
            state='PROGRESS',
            meta={'current': 0, 'total': 100, 'status': 'Finding active keywords...'}
        )
        
        logger.info(f"Task {self.name} [{self.request.id}] started for user {user_id}")
        
        # Get active keywords
        query = db.query(Keyword).filter(Keyword.is_active == True)
        if user_id:
            query = query.filter(Keyword.user_id == user_id)
        
        active_keywords = query.all()
        
        if not active_keywords:
            logger.info("No active keywords found")
            return {
                "status": "completed",
                "message": "No active keywords found",
                "keywords_processed": 0,
                "total_posts_saved": 0,
                "task_id": self.request.id
            }
        
        # Update progress
        self.update_state(
            state='PROGRESS',
            meta={
                'current': 10, 
                'total': 100, 
                'status': f'Found {len(active_keywords)} active keywords, starting crawl...'
            }
        )
        
        # Process each keyword
        keywords_processed = 0
        total_posts_saved = 0
        failed_keywords = []
        
        for i, keyword in enumerate(active_keywords):
            try:
                # Update progress
                progress = 10 + (i / len(active_keywords)) * 80  # 10-90%
                self.update_state(
                    state='PROGRESS',
                    meta={
                        'current': int(progress),
                        'total': 100,
                        'status': f'Processing keyword {i+1}/{len(active_keywords)}: {keyword.keyword}'
                    }
                )
                
                # Start crawl task for this keyword
                crawl_result = crawl_keyword_posts.apply(
                    args=[keyword.id, limit_per_keyword, time_filter, sort, False, 0]
                )
                
                if crawl_result.successful():
                    result_data = crawl_result.result
                    total_posts_saved += result_data.get('posts_saved', 0)
                    keywords_processed += 1
                    logger.info(f"Successfully crawled keyword '{keyword.keyword}': {result_data.get('posts_saved', 0)} posts")
                else:
                    failed_keywords.append(keyword.keyword)
                    logger.error(f"Failed to crawl keyword '{keyword.keyword}': {crawl_result.result}")
                
            except Exception as e:
                failed_keywords.append(keyword.keyword)
                logger.error(f"Error processing keyword '{keyword.keyword}': {e}")
                continue
        
        # Final progress update
        self.update_state(
            state='PROGRESS',
            meta={'current': 100, 'total': 100, 'status': 'Crawl completed'}
        )
        
        result = {
            "status": "completed",
            "message": f"Crawled {keywords_processed} keywords successfully",
            "keywords_processed": keywords_processed,
            "total_keywords": len(active_keywords),
            "total_posts_saved": total_posts_saved,
            "failed_keywords": failed_keywords,
            "task_id": self.request.id
        }
        
        logger.info(f"Task {self.name} [{self.request.id}] completed: {keywords_processed}/{len(active_keywords)} keywords, {total_posts_saved} total posts")
        return result
        
    except Exception as exc:
        logger.error(f"Task {self.name} [{self.request.id}] failed: {exc}")
        raise
    finally:
        if db:
            db.close()


@celery_app.task(bind=True, base=BaseTask, name="crawl_subreddit_posts")
def crawl_subreddit_posts(
    self,
    subreddit_name: str,
    keyword_id: int,
    limit: int = 100,
    sort: str = "hot"
) -> Dict[str, Any]:
    """
    Crawl posts from a specific subreddit and associate with a keyword.
    
    Args:
        subreddit_name: Name of the subreddit to crawl
        keyword_id: ID of the keyword to associate posts with
        limit: Maximum number of posts to retrieve
        sort: Sort method (hot, new, top, rising)
        
    Returns:
        Dictionary containing task result
    """
    db = None
    try:
        # Get database session
        db = get_db_session()
        
        # Update task progress
        self.update_state(
            state='PROGRESS',
            meta={'current': 0, 'total': 100, 'status': f'Starting crawl for r/{subreddit_name}...'}
        )
        
        logger.info(f"Task {self.name} [{self.request.id}] started for r/{subreddit_name}")
        
        # Get keyword from database
        keyword = db.query(Keyword).filter(Keyword.id == keyword_id).first()
        if not keyword:
            raise ValueError(f"Keyword with ID {keyword_id} not found")
        
        # Update progress
        self.update_state(
            state='PROGRESS',
            meta={'current': 20, 'total': 100, 'status': f'Fetching posts from r/{subreddit_name}...'}
        )
        
        # Fetch posts from subreddit
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            posts_data = loop.run_until_complete(
                reddit_client.get_subreddit_posts(
                    subreddit_name=subreddit_name,
                    limit=limit,
                    sort=sort
                )
            )
        finally:
            loop.close()
        
        if not posts_data:
            logger.warning(f"No posts found in r/{subreddit_name}")
            return {
                "status": "completed",
                "message": f"No posts found in r/{subreddit_name}",
                "subreddit": subreddit_name,
                "keyword_id": keyword_id,
                "posts_saved": 0,
                "task_id": self.request.id
            }
        
        # Update progress
        self.update_state(
            state='PROGRESS',
            meta={'current': 50, 'total': 100, 'status': f'Found {len(posts_data)} posts, saving to database...'}
        )
        
        # Save posts to database
        posts_saved = 0
        
        for i, post_data in enumerate(posts_data):
            try:
                # Check if post already exists
                existing_post = db.query(Post).filter(
                    Post.reddit_id == post_data.reddit_id
                ).first()
                
                if existing_post:
                    logger.debug(f"Post {post_data.reddit_id} already exists, skipping")
                    continue
                
                # Create new post
                db_post = Post(
                    keyword_id=keyword_id,
                    reddit_id=post_data.reddit_id,
                    title=post_data.title,
                    content=post_data.content,
                    author=post_data.author,
                    score=post_data.score,
                    num_comments=post_data.num_comments,
                    url=post_data.url,
                    subreddit=post_data.subreddit,
                    post_created_at=post_data.created_at
                )
                
                db.add(db_post)
                db.commit()
                posts_saved += 1
                
                # Update progress
                progress = 50 + (i / len(posts_data)) * 40  # 50-90%
                self.update_state(
                    state='PROGRESS',
                    meta={
                        'current': int(progress),
                        'total': 100,
                        'status': f'Saved post {i+1}/{len(posts_data)}: {post_data.title[:50]}...'
                    }
                )
                
            except IntegrityError:
                db.rollback()
                logger.debug(f"Post {post_data.reddit_id} already exists")
                continue
            except Exception as e:
                logger.error(f"Failed to save post {post_data.reddit_id}: {e}")
                db.rollback()
                continue
        
        result = {
            "status": "completed",
            "message": f"Successfully crawled r/{subreddit_name}",
            "subreddit": subreddit_name,
            "keyword_id": keyword_id,
            "keyword": keyword.keyword,
            "posts_found": len(posts_data),
            "posts_saved": posts_saved,
            "task_id": self.request.id
        }
        
        logger.info(f"Task {self.name} [{self.request.id}] completed for r/{subreddit_name}: {posts_saved} posts")
        return result
        
    except Exception as exc:
        logger.error(f"Task {self.name} [{self.request.id}] failed for r/{subreddit_name}: {exc}")
        raise
    finally:
        if db:
            db.close()


@celery_app.task(bind=True, base=BaseTask, name="test_task_with_retry")
def test_task_with_retry(self, should_fail: bool = False) -> Dict[str, Any]:
    """
    Test task to demonstrate retry functionality and error handling.
    
    Args:
        should_fail: Whether the task should fail to test retry logic
        
    Returns:
        Dictionary containing task result
    """
    try:
        logger.info(f"Test task {self.request.id} started, should_fail={should_fail}")
        
        # Update progress
        self.update_state(
            state='PROGRESS',
            meta={'current': 1, 'total': 3, 'status': 'Processing step 1...'}
        )
        
        if should_fail and self.request.retries < 2:
            # Simulate failure for testing retry logic
            raise Exception(f"Simulated failure (attempt {self.request.retries + 1})")
        
        # Update progress
        self.update_state(
            state='PROGRESS',
            meta={'current': 2, 'total': 3, 'status': 'Processing step 2...'}
        )
        
        # Simulate some work
        import time
        time.sleep(1)
        
        # Final progress update
        self.update_state(
            state='PROGRESS',
            meta={'current': 3, 'total': 3, 'status': 'Completing...'}
        )
        
        result = {
            "status": "success",
            "message": "Test task completed successfully",
            "retries": self.request.retries,
            "task_id": self.request.id
        }
        
        logger.info(f"Test task {self.request.id} completed successfully")
        return result
        
    except Exception as exc:
        logger.error(f"Test task {self.request.id} failed: {exc}")
        raise