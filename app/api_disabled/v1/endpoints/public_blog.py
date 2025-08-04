"""
Public blog API endpoints for the blog site.
These endpoints don't require authentication and are used by the public blog frontend.
"""

import logging
import time
from datetime import datetime, timedelta
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Path
from sqlalchemy.orm import Session
from sqlalchemy import desc, func, and_, or_, extract
from sqlalchemy.sql import text

from app.core.database import get_db
from app.models.blog_content import BlogContent
from app.models.keyword import Keyword
from app.schemas.public_blog import (
    PublicBlogPostListResponse,
    PublicBlogPostSummary,
    PublicBlogPostDetail,
    BlogCategoryResponse,
    BlogTagResponse,
    BlogSearchResponse,
    BlogArchiveResponse,
    BlogStatsResponse,
    RSSFeedResponse,
    RSSFeedItem,
    SitemapResponse,
    SitemapUrl,
    RelatedPostResponse
)

logger = logging.getLogger(__name__)

router = APIRouter()


def _create_excerpt(content: str, max_length: int = 200) -> str:
    """Create excerpt from markdown content."""
    # Remove markdown formatting for excerpt
    import re
    text = re.sub(r'[#*`_\[\]()]', '', content)
    text = re.sub(r'https?://\S+', '', text)  # Remove URLs
    text = ' '.join(text.split())  # Normalize whitespace
    
    if len(text) <= max_length:
        return text
    
    # Find the last complete sentence within the limit
    excerpt = text[:max_length]
    last_period = excerpt.rfind('.')
    last_exclamation = excerpt.rfind('!')
    last_question = excerpt.rfind('?')
    
    last_sentence_end = max(last_period, last_exclamation, last_question)
    
    if last_sentence_end > max_length * 0.7:  # If we have a good sentence break
        return excerpt[:last_sentence_end + 1]
    else:
        return excerpt.rstrip() + "..."


def _parse_tags(tags_str: Optional[str]) -> List[str]:
    """Parse comma-separated tags string into list."""
    if not tags_str:
        return []
    return [tag.strip() for tag in tags_str.split(',') if tag.strip()]


def _calculate_read_time(word_count: int) -> int:
    """Calculate estimated read time in minutes."""
    return max(1, word_count // 200)  # ~200 words per minute


@router.get("/posts", response_model=PublicBlogPostListResponse)
async def list_blog_posts(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(10, ge=1, le=50, description="Posts per page"),
    category: Optional[str] = Query(None, description="Filter by category (keyword)"),
    tag: Optional[str] = Query(None, description="Filter by tag"),
    sort: str = Query("latest", pattern="^(latest|oldest|popular)$", description="Sort order"),
    db: Session = Depends(get_db)
):
    """
    Get paginated list of published blog posts.
    """
    try:
        # Build base query for published posts only
        query = db.query(BlogContent).filter(BlogContent.status == "published")
        
        # Apply category filter (based on keyword)
        if category:
            query = query.join(Keyword).filter(Keyword.keyword == category)
        
        # Apply tag filter
        if tag:
            query = query.filter(BlogContent.tags.contains(tag))
        
        # Apply sorting
        if sort == "latest":
            query = query.order_by(desc(BlogContent.created_at))
        elif sort == "oldest":
            query = query.order_by(BlogContent.created_at)
        elif sort == "popular":
            # Sort by word count as a proxy for popularity
            query = query.order_by(desc(BlogContent.word_count))
        
        # Get total count
        total = query.count()
        
        # Apply pagination
        posts = query.offset((page - 1) * size).limit(size).all()
        
        # Calculate pagination info
        pages = (total + size - 1) // size
        has_next = page < pages
        has_prev = page > 1
        
        # Convert to response format
        post_summaries = []
        for post in posts:
            tags = _parse_tags(post.tags)
            excerpt = _create_excerpt(post.content)
            
            post_summaries.append(PublicBlogPostSummary(
                id=post.id,
                title=post.title,
                slug=post.slug or f"post-{post.id}",
                meta_description=post.meta_description,
                tags=tags,
                featured_image_url=post.featured_image_url,
                word_count=post.word_count or 0,
                estimated_read_time=_calculate_read_time(post.word_count or 0),
                published_at=post.created_at,
                excerpt=excerpt
            ))
        
        return PublicBlogPostListResponse(
            posts=post_summaries,
            total=total,
            page=page,
            size=size,
            pages=pages,
            has_next=has_next,
            has_prev=has_prev
        )
        
    except Exception as e:
        logger.error(f"Error listing blog posts: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve blog posts")


@router.get("/posts/{slug}", response_model=PublicBlogPostDetail)
async def get_blog_post_by_slug(
    slug: str,
    db: Session = Depends(get_db)
):
    """
    Get a specific blog post by slug.
    """
    try:
        post = db.query(BlogContent).filter(
            and_(
                BlogContent.slug == slug,
                BlogContent.status == "published"
            )
        ).first()
        
        if not post:
            raise HTTPException(status_code=404, detail="Blog post not found")
        
        tags = _parse_tags(post.tags)
        
        return PublicBlogPostDetail(
            id=post.id,
            title=post.title,
            content=post.content,
            slug=post.slug or f"post-{post.id}",
            meta_description=post.meta_description,
            tags=tags,
            featured_image_url=post.featured_image_url,
            word_count=post.word_count or 0,
            estimated_read_time=_calculate_read_time(post.word_count or 0),
            published_at=post.created_at,
            updated_at=post.updated_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting blog post by slug: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve blog post")


@router.get("/categories", response_model=List[BlogCategoryResponse])
async def list_blog_categories(db: Session = Depends(get_db)):
    """
    Get list of blog categories (based on keywords with published posts).
    """
    try:
        # Get keywords that have published blog content
        categories = db.query(
            Keyword.keyword,
            func.count(BlogContent.id).label('count')
        ).join(
            BlogContent, Keyword.id == BlogContent.keyword_id
        ).filter(
            BlogContent.status == "published"
        ).group_by(
            Keyword.keyword
        ).order_by(
            desc('count')
        ).all()
        
        return [
            BlogCategoryResponse(
                name=category.keyword.replace('_', ' ').title(),
                slug=category.keyword,
                count=category.count
            )
            for category in categories
        ]
        
    except Exception as e:
        logger.error(f"Error listing blog categories: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve categories")


@router.get("/tags", response_model=List[BlogTagResponse])
async def list_blog_tags(db: Session = Depends(get_db)):
    """
    Get list of blog tags with post counts.
    """
    try:
        # Get all published posts with tags
        posts_with_tags = db.query(BlogContent.tags).filter(
            and_(
                BlogContent.status == "published",
                BlogContent.tags.isnot(None),
                BlogContent.tags != ""
            )
        ).all()
        
        # Count tag occurrences
        tag_counts = {}
        for post in posts_with_tags:
            tags = _parse_tags(post.tags)
            for tag in tags:
                tag_counts[tag] = tag_counts.get(tag, 0) + 1
        
        # Sort by count and convert to response format
        sorted_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)
        
        return [
            BlogTagResponse(
                name=tag,
                slug=tag.lower().replace(' ', '-'),
                count=count
            )
            for tag, count in sorted_tags
        ]
        
    except Exception as e:
        logger.error(f"Error listing blog tags: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve tags")


@router.get("/search", response_model=BlogSearchResponse)
async def search_blog_posts(
    q: str = Query(..., min_length=1, description="Search query"),
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(10, ge=1, le=50, description="Posts per page"),
    db: Session = Depends(get_db)
):
    """
    Search blog posts by title, content, and tags.
    """
    try:
        start_time = time.time()
        
        # Build search query
        search_term = f"%{q}%"
        query = db.query(BlogContent).filter(
            and_(
                BlogContent.status == "published",
                or_(
                    BlogContent.title.ilike(search_term),
                    BlogContent.content.ilike(search_term),
                    BlogContent.tags.ilike(search_term),
                    BlogContent.meta_description.ilike(search_term)
                )
            )
        ).order_by(desc(BlogContent.created_at))
        
        # Get total count
        total = query.count()
        
        # Apply pagination
        posts = query.offset((page - 1) * size).limit(size).all()
        
        # Calculate pagination info
        pages = (total + size - 1) // size
        
        # Convert to response format
        post_summaries = []
        for post in posts:
            tags = _parse_tags(post.tags)
            excerpt = _create_excerpt(post.content)
            
            post_summaries.append(PublicBlogPostSummary(
                id=post.id,
                title=post.title,
                slug=post.slug or f"post-{post.id}",
                meta_description=post.meta_description,
                tags=tags,
                featured_image_url=post.featured_image_url,
                word_count=post.word_count or 0,
                estimated_read_time=_calculate_read_time(post.word_count or 0),
                published_at=post.created_at,
                excerpt=excerpt
            ))
        
        search_time_ms = int((time.time() - start_time) * 1000)
        
        return BlogSearchResponse(
            posts=post_summaries,
            total=total,
            query=q,
            page=page,
            size=size,
            pages=pages,
            search_time_ms=search_time_ms
        )
        
    except Exception as e:
        logger.error(f"Error searching blog posts: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to search blog posts")


@router.get("/archive/{year}/{month}", response_model=BlogArchiveResponse)
async def get_blog_archive(
    year: int = Path(..., ge=2020, le=2030, description="Year"),
    month: int = Path(..., ge=1, le=12, description="Month"),
    db: Session = Depends(get_db)
):
    """
    Get blog posts for a specific month and year.
    """
    try:
        # Query posts for the specific month/year
        posts = db.query(BlogContent).filter(
            and_(
                BlogContent.status == "published",
                extract('year', BlogContent.created_at) == year,
                extract('month', BlogContent.created_at) == month
            )
        ).order_by(desc(BlogContent.created_at)).all()
        
        # Convert to response format
        post_summaries = []
        for post in posts:
            tags = _parse_tags(post.tags)
            excerpt = _create_excerpt(post.content)
            
            post_summaries.append(PublicBlogPostSummary(
                id=post.id,
                title=post.title,
                slug=post.slug or f"post-{post.id}",
                meta_description=post.meta_description,
                tags=tags,
                featured_image_url=post.featured_image_url,
                word_count=post.word_count or 0,
                estimated_read_time=_calculate_read_time(post.word_count or 0),
                published_at=post.created_at,
                excerpt=excerpt
            ))
        
        return BlogArchiveResponse(
            year=year,
            month=month,
            count=len(posts),
            posts=post_summaries
        )
        
    except Exception as e:
        logger.error(f"Error getting blog archive: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve archive")


@router.get("/stats", response_model=BlogStatsResponse)
async def get_blog_stats(db: Session = Depends(get_db)):
    """
    Get blog statistics.
    """
    try:
        # Get basic stats
        stats = db.query(
            func.count(BlogContent.id).label('total_posts'),
            func.sum(BlogContent.word_count).label('total_words'),
            func.max(BlogContent.created_at).label('latest_post_date'),
            func.avg(BlogContent.word_count).label('avg_word_count')
        ).filter(BlogContent.status == "published").first()
        
        # Count unique tags
        posts_with_tags = db.query(BlogContent.tags).filter(
            and_(
                BlogContent.status == "published",
                BlogContent.tags.isnot(None),
                BlogContent.tags != ""
            )
        ).all()
        
        unique_tags = set()
        for post in posts_with_tags:
            tags = _parse_tags(post.tags)
            unique_tags.update(tags)
        
        return BlogStatsResponse(
            total_posts=stats.total_posts or 0,
            total_words=int(stats.total_words or 0),
            total_tags=len(unique_tags),
            latest_post_date=stats.latest_post_date,
            average_read_time=_calculate_read_time(int(stats.avg_word_count or 0))
        )
        
    except Exception as e:
        logger.error(f"Error getting blog stats: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve stats")


@router.get("/posts/{post_id}/related", response_model=List[RelatedPostResponse])
async def get_related_posts(
    post_id: int,
    limit: int = Query(5, ge=1, le=10, description="Number of related posts"),
    db: Session = Depends(get_db)
):
    """
    Get related posts based on tags and category.
    """
    try:
        # Get the current post
        current_post = db.query(BlogContent).filter(
            and_(
                BlogContent.id == post_id,
                BlogContent.status == "published"
            )
        ).first()
        
        if not current_post:
            raise HTTPException(status_code=404, detail="Post not found")
        
        current_tags = _parse_tags(current_post.tags)
        
        # Find related posts by tags and category
        related_posts = db.query(BlogContent).filter(
            and_(
                BlogContent.id != post_id,
                BlogContent.status == "published",
                or_(
                    BlogContent.keyword_id == current_post.keyword_id,  # Same category
                    *[BlogContent.tags.contains(tag) for tag in current_tags] if current_tags else [False]
                )
            )
        ).order_by(desc(BlogContent.created_at)).limit(limit * 2).all()  # Get more to calculate similarity
        
        # Calculate similarity scores and sort
        related_with_scores = []
        for post in related_posts:
            post_tags = _parse_tags(post.tags)
            
            # Calculate similarity based on common tags and same category
            similarity_score = 0.0
            
            # Same category bonus
            if post.keyword_id == current_post.keyword_id:
                similarity_score += 0.5
            
            # Common tags bonus
            if current_tags and post_tags:
                common_tags = set(current_tags) & set(post_tags)
                similarity_score += len(common_tags) / max(len(current_tags), len(post_tags))
            
            if similarity_score > 0:
                excerpt = _create_excerpt(post.content)
                related_with_scores.append((post, similarity_score, excerpt))
        
        # Sort by similarity score and take top results
        related_with_scores.sort(key=lambda x: x[1], reverse=True)
        top_related = related_with_scores[:limit]
        
        return [
            RelatedPostResponse(
                id=post.id,
                title=post.title,
                slug=post.slug or f"post-{post.id}",
                excerpt=excerpt,
                published_at=post.created_at,
                similarity_score=score
            )
            for post, score, excerpt in top_related
        ]
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting related posts: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve related posts")


@router.get("/rss", response_model=RSSFeedResponse)
async def get_rss_feed(
    limit: int = Query(20, ge=1, le=50, description="Number of posts in feed"),
    db: Session = Depends(get_db)
):
    """
    Generate RSS feed for the blog.
    """
    try:
        # Get recent published posts
        posts = db.query(BlogContent).filter(
            BlogContent.status == "published"
        ).order_by(desc(BlogContent.created_at)).limit(limit).all()
        
        # Create RSS items
        rss_items = []
        for post in posts:
            excerpt = _create_excerpt(post.content, 300)
            
            rss_items.append(RSSFeedItem(
                title=post.title,
                link=f"/posts/{post.slug or f'post-{post.id}'}",
                description=post.meta_description or excerpt,
                pub_date=post.created_at,
                guid=f"post-{post.id}"
            ))
        
        return RSSFeedResponse(
            title="Reddit Trends Blog",
            link="/",
            description="Latest trends and insights from Reddit discussions",
            language="en-us",
            last_build_date=datetime.utcnow(),
            items=rss_items
        )
        
    except Exception as e:
        logger.error(f"Error generating RSS feed: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to generate RSS feed")


@router.get("/sitemap", response_model=SitemapResponse)
async def get_sitemap(db: Session = Depends(get_db)):
    """
    Generate sitemap for the blog.
    """
    try:
        # Get all published posts
        posts = db.query(BlogContent).filter(
            BlogContent.status == "published"
        ).order_by(desc(BlogContent.created_at)).all()
        
        # Create sitemap URLs
        urls = [
            # Homepage
            SitemapUrl(
                loc="/",
                lastmod=datetime.utcnow(),
                changefreq="daily",
                priority=1.0
            ),
            # Posts index
            SitemapUrl(
                loc="/posts",
                lastmod=datetime.utcnow(),
                changefreq="daily",
                priority=0.9
            )
        ]
        
        # Add individual posts
        for post in posts:
            urls.append(SitemapUrl(
                loc=f"/posts/{post.slug or f'post-{post.id}'}",
                lastmod=post.updated_at or post.created_at,
                changefreq="weekly",
                priority=0.8
            ))
        
        return SitemapResponse(urls=urls)
        
    except Exception as e:
        logger.error(f"Error generating sitemap: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to generate sitemap")