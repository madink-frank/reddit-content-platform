"""
Post service for managing Reddit posts and comments.
Enhanced with performance optimizations and caching.
"""

from typing import List, Optional, Tuple
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, desc, asc, func
from datetime import datetime

from app.models.post import Post, Comment
from app.models.keyword import Keyword
from app.schemas.post import PostQueryParams, PostResponse, PostDetailResponse, PostListResponse, CommentResponse
from app.core.database import get_db
from app.core.cache_optimization import cache_frequent, cache_stable, smart_cache
from app.core.database_optimization import OptimizedPostService


class PostService:
    """Service for post-related operations with performance optimizations."""

    def __init__(self, db: Session):
        self.db = db
        self.optimized_service = OptimizedPostService(db)

    async def get_posts_paginated(
        self, 
        user_id: int, 
        query_params: PostQueryParams
    ) -> PostListResponse:
        """
        Get paginated list of posts with filtering and sorting.
        Only returns posts from keywords owned by the user.
        """
        # Base query with user's keywords only
        base_query = (
            self.db.query(Post)
            .join(Keyword)
            .filter(Keyword.user_id == user_id)
        )

        # Apply filters
        base_query = self._apply_filters(base_query, query_params)

        # Get total count before pagination
        total = base_query.count()

        # Apply sorting
        base_query = self._apply_sorting(base_query, query_params)

        # Apply pagination
        offset = (query_params.page - 1) * query_params.per_page
        posts = base_query.offset(offset).limit(query_params.per_page).all()

        # Calculate pagination metadata
        total_pages = (total + query_params.per_page - 1) // query_params.per_page
        has_next = query_params.page < total_pages
        has_prev = query_params.page > 1

        return PostListResponse(
            posts=[PostResponse.from_orm(post) for post in posts],
            total=total,
            page=query_params.page,
            per_page=query_params.per_page,
            total_pages=total_pages,
            has_next=has_next,
            has_prev=has_prev
        )

    async def get_post_by_id(self, post_id: int, user_id: int) -> Optional[PostDetailResponse]:
        """
        Get a specific post by ID with comments.
        Only returns post if it belongs to user's keywords.
        """
        post = (
            self.db.query(Post)
            .join(Keyword)
            .filter(
                and_(
                    Post.id == post_id,
                    Keyword.user_id == user_id
                )
            )
            .options(joinedload(Post.comments))
            .first()
        )

        if not post:
            return None

        # Convert comments to response format
        comments = [CommentResponse.from_orm(comment) for comment in post.comments]
        
        # Create detailed response
        post_detail = PostDetailResponse.from_orm(post)
        post_detail.comments = comments
        
        return post_detail

    async def get_posts_by_keyword(
        self, 
        keyword_id: int, 
        user_id: int,
        page: int = 1,
        per_page: int = 10,
        sort_by: str = "created_at",
        sort_order: str = "desc"
    ) -> PostListResponse:
        """
        Get posts for a specific keyword.
        Only returns posts if keyword belongs to the user.
        """
        # Verify keyword belongs to user
        keyword = (
            self.db.query(Keyword)
            .filter(and_(Keyword.id == keyword_id, Keyword.user_id == user_id))
            .first()
        )

        if not keyword:
            return PostListResponse(
                posts=[],
                total=0,
                page=page,
                per_page=per_page,
                total_pages=0,
                has_next=False,
                has_prev=False
            )

        # Create query params for filtering
        query_params = PostQueryParams(
            page=page,
            per_page=per_page,
            keyword_id=keyword_id,
            sort_by=sort_by,
            sort_order=sort_order
        )

        return await self.get_posts_paginated(user_id, query_params)

    async def search_posts(
        self,
        user_id: int,
        search_term: str,
        page: int = 1,
        per_page: int = 10,
        sort_by: str = "created_at",
        sort_order: str = "desc"
    ) -> PostListResponse:
        """
        Search posts by title and content.
        Only searches in posts from user's keywords.
        """
        query_params = PostQueryParams(
            page=page,
            per_page=per_page,
            search=search_term,
            sort_by=sort_by,
            sort_order=sort_order
        )

        return await self.get_posts_paginated(user_id, query_params)

    @cache_frequent
    async def get_post_statistics(self, user_id: int) -> dict:
        """
        Get statistics about user's posts with caching.
        """
        # Use optimized query
        return self.optimized_service.get_post_statistics_optimized(user_id)
    
    async def get_posts_with_metrics(
        self, 
        user_id: int, 
        keyword_id: Optional[int] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[dict]:
        """
        Get posts with metrics using optimized queries.
        """
        cache_key = f"posts_with_metrics:{user_id}:{keyword_id}:{limit}:{offset}"
        
        return await smart_cache.get_or_set(
            cache_key,
            self.optimized_service.get_posts_with_metrics_optimized,
            cache_frequent.config,
            user_id, keyword_id, limit, offset
        )
    
    @cache_stable
    async def get_trending_posts(
        self, 
        user_id: int, 
        hours: int = 24,
        limit: int = 20
    ) -> List[dict]:
        """
        Get trending posts with caching.
        """
        return self.optimized_service.get_trending_posts_optimized(user_id, hours, limit)

    def _apply_filters(self, query, params: PostQueryParams):
        """Apply filters to the query based on parameters."""
        
        if params.keyword_id:
            query = query.filter(Post.keyword_id == params.keyword_id)
        
        if params.subreddit:
            query = query.filter(Post.subreddit.ilike(f"%{params.subreddit}%"))
        
        if params.author:
            query = query.filter(Post.author.ilike(f"%{params.author}%"))
        
        if params.search:
            search_filter = or_(
                Post.title.ilike(f"%{params.search}%"),
                Post.content.ilike(f"%{params.search}%")
            )
            query = query.filter(search_filter)
        
        if params.min_score is not None:
            query = query.filter(Post.score >= params.min_score)
        
        if params.max_score is not None:
            query = query.filter(Post.score <= params.max_score)
        
        if params.date_from:
            query = query.filter(Post.post_created_at >= params.date_from)
        
        if params.date_to:
            query = query.filter(Post.post_created_at <= params.date_to)
        
        return query

    def _apply_sorting(self, query, params: PostQueryParams):
        """Apply sorting to the query."""
        
        # Map sort fields to model attributes
        sort_fields = {
            'created_at': Post.created_at,
            'post_created_at': Post.post_created_at,
            'score': Post.score,
            'num_comments': Post.num_comments,
            'title': Post.title,
            'author': Post.author,
            'subreddit': Post.subreddit
        }
        
        sort_field = sort_fields.get(params.sort_by, Post.created_at)
        
        if params.sort_order == 'desc':
            query = query.order_by(desc(sort_field))
        else:
            query = query.order_by(asc(sort_field))
        
        return query


def get_post_service(db: Session = None) -> PostService:
    """Get post service instance."""
    if db is None:
        db = next(get_db())
    return PostService(db)