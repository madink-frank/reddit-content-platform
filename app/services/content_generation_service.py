"""
Content generation service for creating markdown blog posts from trend data.
"""

import logging
import re
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.models.keyword import Keyword
from app.models.post import Post
from app.models.blog_content import BlogContent
from app.services.template_service import TemplateService
from app.services.trend_analysis_service import TrendAnalysisService
from app.schemas.blog_content import ContentGenerationRequest

logger = logging.getLogger(__name__)


class ContentGenerationService:
    """
    Service for generating markdown blog content from Reddit trend data.
    """
    
    def __init__(self):
        self.template_service = TemplateService()
        self.trend_service = TrendAnalysisService()
    
    async def generate_blog_content(
        self, 
        request: ContentGenerationRequest, 
        db: Session
    ) -> Optional[BlogContent]:
        """
        Generate blog content based on trend data and user preferences.
        
        Args:
            request: Content generation request parameters
            db: Database session
            
        Returns:
            Generated BlogContent object or None if generation failed
        """
        try:
            logger.info(f"Starting content generation for keyword_id: {request.keyword_id}")
            
            # Get keyword information
            keyword = db.query(Keyword).filter(Keyword.id == request.keyword_id).first()
            if not keyword:
                logger.error(f"Keyword not found: {request.keyword_id}")
                return None
            
            # Get trend data
            trend_data = None
            if request.include_trends:
                trend_data = await self.trend_service.analyze_keyword_trends(
                    request.keyword_id, db, force_refresh=False
                )
            
            # Get top posts
            top_posts = []
            if request.include_top_posts:
                top_posts = self._get_top_posts(request.keyword_id, request.max_posts, db)
            
            # Generate insights
            insights = self._generate_insights(keyword.keyword, trend_data, top_posts)
            
            # Prepare template context
            context = self._prepare_template_context(
                keyword=keyword,
                trend_data=trend_data,
                top_posts=top_posts,
                insights=insights,
                custom_prompt=request.custom_prompt
            )
            
            # Generate title and meta description
            title = self._generate_title(keyword.keyword, trend_data)
            meta_description = self._generate_meta_description(keyword.keyword, trend_data)
            
            # Add title and meta to context
            context.update({
                "title": title,
                "meta_description": meta_description
            })
            
            # Render template
            content = self.template_service.render_template(request.template_type, context)
            if not content:
                logger.error(f"Failed to render template: {request.template_type}")
                return None
            
            # Post-process content
            content = self._post_process_content(content)
            
            # Generate additional metadata
            word_count = self._count_words(content)
            slug = self._generate_slug(title)
            tags = self._generate_tags(keyword.keyword, trend_data, top_posts)
            
            # Create BlogContent object
            blog_content = BlogContent(
                keyword_id=request.keyword_id,
                title=title,
                content=content,
                template_used=request.template_type,
                generated_at=datetime.utcnow(),
                word_count=word_count,
                slug=slug,
                meta_description=meta_description,
                tags=",".join(tags) if tags else None,
                status="draft"
            )
            
            # Save to database
            db.add(blog_content)
            db.commit()
            db.refresh(blog_content)
            
            logger.info(f"Successfully generated blog content with ID: {blog_content.id}")
            return blog_content
            
        except Exception as e:
            logger.error(f"Error generating blog content: {str(e)}")
            db.rollback()
            return None
    
    def _get_top_posts(self, keyword_id: int, max_posts: int, db: Session) -> List[Post]:
        """Get top posts for a keyword based on engagement score."""
        try:
            posts = db.query(Post).filter(
                Post.keyword_id == keyword_id
            ).order_by(
                desc(Post.score),
                desc(Post.num_comments)
            ).limit(max_posts).all()
            
            return posts
            
        except Exception as e:
            logger.error(f"Error getting top posts: {str(e)}")
            return []
    
    def _generate_insights(
        self, 
        keyword: str, 
        trend_data: Optional[Dict[str, Any]], 
        top_posts: List[Post]
    ) -> List[str]:
        """Generate insights based on trend data and posts."""
        insights = []
        
        try:
            if trend_data:
                # Trend direction insights
                direction = trend_data.get("trend_direction", "stable")
                if direction == "rising":
                    insights.append(f"Interest in {keyword} is growing rapidly on Reddit")
                elif direction == "falling":
                    insights.append(f"Discussion around {keyword} is declining")
                else:
                    insights.append(f"Interest in {keyword} remains stable")
                
                # Engagement insights
                engagement = trend_data.get("avg_engagement_score", 0)
                if engagement > 0.7:
                    insights.append("Community engagement is exceptionally high")
                elif engagement > 0.4:
                    insights.append("The community shows moderate engagement")
                else:
                    insights.append("This topic is emerging with growing interest")
                
                # Volume insights
                total_posts = trend_data.get("total_posts", 0)
                if total_posts > 100:
                    insights.append(f"High discussion volume with {total_posts} posts analyzed")
                elif total_posts > 20:
                    insights.append(f"Moderate discussion activity with {total_posts} posts")
                else:
                    insights.append("Niche topic with focused community discussion")
            
            # Post-based insights
            if top_posts:
                avg_score = sum(post.score for post in top_posts) / len(top_posts)
                avg_comments = sum(post.num_comments for post in top_posts) / len(top_posts)
                
                if avg_score > 1000:
                    insights.append("Posts consistently receive high upvotes")
                if avg_comments > 50:
                    insights.append("Topics generate extensive discussion and debate")
                
                # Author diversity
                authors = set(post.author for post in top_posts if post.author)
                if len(authors) == len(top_posts):
                    insights.append("Diverse range of community members participating")
                elif len(authors) < len(top_posts) / 2:
                    insights.append("Discussion driven by a core group of active users")
            
            return insights[:5]  # Limit to top 5 insights
            
        except Exception as e:
            logger.error(f"Error generating insights: {str(e)}")
            return ["Analysis reveals interesting community patterns around this topic"]
    
    def _prepare_template_context(
        self,
        keyword: Keyword,
        trend_data: Optional[Dict[str, Any]],
        top_posts: List[Post],
        insights: List[str],
        custom_prompt: Optional[str]
    ) -> Dict[str, Any]:
        """Prepare context variables for template rendering."""
        context = {
            "keyword": keyword.keyword,
            "keyword_id": keyword.id,
            "trend_data": trend_data,
            "top_posts": top_posts,
            "insights": insights,
            "generated_at": datetime.utcnow().isoformat(),
        }
        
        # Add custom conclusion if custom prompt provided
        if custom_prompt:
            context["conclusion"] = custom_prompt
        
        return context
    
    def _generate_title(self, keyword: str, trend_data: Optional[Dict[str, Any]]) -> str:
        """Generate an engaging title for the blog post."""
        try:
            keyword_title = keyword.replace("_", " ").title()
            
            if trend_data:
                direction = trend_data.get("trend_direction", "stable")
                total_posts = trend_data.get("total_posts", 0)
                
                if direction == "rising":
                    return f"Why {keyword_title} is Trending on Reddit Right Now"
                elif direction == "falling":
                    return f"The Decline of {keyword_title} Discussions on Reddit"
                elif total_posts > 100:
                    return f"{keyword_title}: What Reddit's {total_posts}+ Posts Reveal"
                else:
                    return f"Reddit's Take on {keyword_title}: Community Insights"
            else:
                return f"Understanding {keyword_title} Through Reddit Discussions"
                
        except Exception as e:
            logger.error(f"Error generating title: {str(e)}")
            return f"Reddit Analysis: {keyword.replace('_', ' ').title()}"
    
    def _generate_meta_description(
        self, 
        keyword: str, 
        trend_data: Optional[Dict[str, Any]]
    ) -> str:
        """Generate SEO meta description."""
        try:
            keyword_clean = keyword.replace("_", " ")
            
            if trend_data:
                total_posts = trend_data.get("total_posts", 0)
                direction = trend_data.get("trend_direction", "stable")
                
                if total_posts > 0:
                    return f"Analysis of {total_posts} Reddit posts about {keyword_clean}. Discover trending topics, community sentiment, and key insights from Reddit discussions."
                else:
                    return f"Comprehensive analysis of Reddit discussions about {keyword_clean}. Explore community insights and trending topics."
            else:
                return f"Explore what Reddit users are saying about {keyword_clean}. Community insights, trending discussions, and key takeaways."
                
        except Exception as e:
            logger.error(f"Error generating meta description: {str(e)}")
            return f"Reddit community analysis and insights about {keyword.replace('_', ' ')}"
    
    def _post_process_content(self, content: str) -> str:
        """Post-process generated content for quality and formatting."""
        try:
            # Remove excessive whitespace
            content = re.sub(r'\n\s*\n\s*\n', '\n\n', content)
            
            # Ensure proper markdown formatting
            content = re.sub(r'^(#{1,6})\s*(.+)$', r'\1 \2', content, flags=re.MULTILINE)
            
            # Fix list formatting
            content = re.sub(r'^(\s*)-\s*(.+)$', r'\1- \2', content, flags=re.MULTILINE)
            
            # Remove empty sections (sections with no content between headers)
            content = re.sub(r'(#{1,6}\s*[^\n]*\n)\s*\n\s*(#{1,6})', r'\1\n\2', content)
            
            # Ensure content ends with newline
            if not content.endswith('\n'):
                content += '\n'
            
            return content.strip()
            
        except Exception as e:
            logger.error(f"Error post-processing content: {str(e)}")
            return content
    
    def _count_words(self, content: str) -> int:
        """Count words in content."""
        try:
            # Remove markdown formatting for accurate word count
            text = re.sub(r'[#*`_\[\]()]', '', content)
            text = re.sub(r'https?://\S+', '', text)  # Remove URLs
            words = text.split()
            return len(words)
        except Exception as e:
            logger.error(f"Error counting words: {str(e)}")
            return 0
    
    def _generate_slug(self, title: str) -> str:
        """Generate URL-friendly slug from title."""
        try:
            # Convert to lowercase and replace spaces with hyphens
            slug = title.lower()
            slug = re.sub(r'[^\w\s-]', '', slug)  # Remove special characters
            slug = re.sub(r'[-\s]+', '-', slug)   # Replace spaces and multiple hyphens
            slug = slug.strip('-')                # Remove leading/trailing hyphens
            
            # Limit length
            if len(slug) > 60:
                slug = slug[:60].rsplit('-', 1)[0]
            
            return slug
            
        except Exception as e:
            logger.error(f"Error generating slug: {str(e)}")
            return "reddit-analysis"
    
    def _generate_tags(
        self, 
        keyword: str, 
        trend_data: Optional[Dict[str, Any]], 
        top_posts: List[Post]
    ) -> List[str]:
        """Generate relevant tags for the content."""
        tags = set()
        
        try:
            # Add keyword-based tags
            tags.add(keyword.replace("_", " "))
            tags.add("reddit")
            tags.add("analysis")
            
            # Add trend-based tags
            if trend_data:
                direction = trend_data.get("trend_direction", "stable")
                tags.add(f"trending-{direction}")
                
                # Add top keywords as tags
                top_keywords = trend_data.get("top_keywords", [])
                for kw_data in top_keywords[:3]:  # Top 3 keywords
                    if isinstance(kw_data, dict) and "keyword" in kw_data:
                        tag = kw_data["keyword"].lower().replace(" ", "-")
                        if len(tag) > 2 and tag not in tags:
                            tags.add(tag)
            
            # Add content type tags
            tags.add("community-insights")
            tags.add("social-media")
            
            # Convert to list and limit
            return list(tags)[:8]  # Limit to 8 tags
            
        except Exception as e:
            logger.error(f"Error generating tags: {str(e)}")
            return ["reddit", "analysis", keyword.replace("_", " ")]
    
    async def preview_content(
        self, 
        request: ContentGenerationRequest, 
        db: Session
    ) -> Optional[Dict[str, Any]]:
        """
        Generate a preview of content without saving to database.
        
        Args:
            request: Content generation request
            db: Database session
            
        Returns:
            Preview data or None if generation failed
        """
        try:
            # Get keyword
            keyword = db.query(Keyword).filter(Keyword.id == request.keyword_id).first()
            if not keyword:
                return None
            
            # Get limited data for preview
            trend_data = None
            if request.include_trends:
                trend_data = await self.trend_service.get_cached_trend_data(request.keyword_id)
            
            top_posts = self._get_top_posts(request.keyword_id, min(request.max_posts, 3), db)
            
            # Generate preview title and description
            title = self._generate_title(keyword.keyword, trend_data)
            meta_description = self._generate_meta_description(keyword.keyword, trend_data)
            
            # Generate content preview (first 500 chars)
            insights = self._generate_insights(keyword.keyword, trend_data, top_posts)
            context = self._prepare_template_context(
                keyword=keyword,
                trend_data=trend_data,
                top_posts=top_posts,
                insights=insights,
                custom_prompt=request.custom_prompt
            )
            context.update({"title": title, "meta_description": meta_description})
            
            content = self.template_service.render_template(request.template_type, context)
            if not content:
                return None
            
            content_preview = content[:500] + "..." if len(content) > 500 else content
            word_count = self._count_words(content)
            estimated_read_time = max(1, word_count // 200)  # ~200 words per minute
            tags = self._generate_tags(keyword.keyword, trend_data, top_posts)
            
            return {
                "title": title,
                "content_preview": content_preview,
                "word_count": word_count,
                "estimated_read_time": estimated_read_time,
                "tags": tags,
                "template_used": request.template_type
            }
            
        except Exception as e:
            logger.error(f"Error generating content preview: {str(e)}")
            return None