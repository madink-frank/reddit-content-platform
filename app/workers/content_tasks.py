"""
Celery tasks for content generation operations.
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from celery import current_task
from sqlalchemy.orm import Session

from app.core.celery_app import celery_app
from app.core.database import get_db
from app.services.content_generation_service import ContentGenerationService
from app.schemas.blog_content import ContentGenerationRequest
from app.models.blog_content import BlogContent
from app.models.process_log import ProcessLog

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, name="generate_blog_content")
def generate_blog_content_task(
    self,
    keyword_id: int,
    template_type: str = "default",
    include_trends: bool = True,
    include_top_posts: bool = True,
    max_posts: int = 10,
    custom_prompt: Optional[str] = None,
    user_id: Optional[int] = None
) -> Dict[str, Any]:
    """
    Celery task for generating blog content.
    
    Args:
        keyword_id: ID of the keyword to generate content for
        template_type: Template type to use
        include_trends: Whether to include trend analysis
        include_top_posts: Whether to include top posts
        max_posts: Maximum number of posts to include
        custom_prompt: Custom generation prompt
        user_id: User ID for logging purposes
        
    Returns:
        Task result with generated content information
    """
    task_id = self.request.id
    db = next(get_db())
    
    try:
        logger.info(f"Starting content generation task {task_id} for keyword_id: {keyword_id}")
        
        # Update task progress
        self.update_state(
            state='PROGRESS',
            meta={'progress': 10, 'message': 'Initializing content generation...'}
        )
        
        # Create process log
        process_log = ProcessLog(
            user_id=user_id,
            task_type="content_generation",
            status="running",
            task_id=task_id
        )
        db.add(process_log)
        db.commit()
        
        # Initialize content generation service
        content_service = ContentGenerationService()
        
        # Create generation request
        request = ContentGenerationRequest(
            keyword_id=keyword_id,
            template_type=template_type,
            include_trends=include_trends,
            include_top_posts=include_top_posts,
            max_posts=max_posts,
            custom_prompt=custom_prompt
        )
        
        # Update progress
        self.update_state(
            state='PROGRESS',
            meta={'progress': 30, 'message': 'Analyzing trend data...'}
        )
        
        # Generate content (run async function in sync context)
        import asyncio
        blog_content = asyncio.run(content_service.generate_blog_content(request, db))
        
        if not blog_content:
            # Update process log with failure
            process_log.status = "failed"
            process_log.error_message = "Content generation failed"
            process_log.completed_at = datetime.utcnow()
            db.commit()
            
            return {
                'status': 'FAILURE',
                'error': 'Content generation failed',
                'task_id': task_id
            }
        
        # Update progress
        self.update_state(
            state='PROGRESS',
            meta={'progress': 90, 'message': 'Finalizing content...'}
        )
        
        # Update process log with success
        process_log.status = "completed"
        process_log.completed_at = datetime.utcnow()
        db.commit()
        
        # Prepare result
        result = {
            'status': 'SUCCESS',
            'task_id': task_id,
            'blog_content_id': blog_content.id,
            'title': blog_content.title,
            'word_count': blog_content.word_count,
            'template_used': blog_content.template_used,
            'generated_at': blog_content.generated_at.isoformat(),
            'message': 'Content generated successfully'
        }
        
        logger.info(f"Content generation task {task_id} completed successfully")
        return result
        
    except Exception as e:
        logger.error(f"Error in content generation task {task_id}: {str(e)}")
        
        # Update process log with error
        try:
            process_log.status = "failed"
            process_log.error_message = str(e)
            process_log.completed_at = datetime.utcnow()
            db.commit()
        except:
            pass
        
        # Update task state
        self.update_state(
            state='FAILURE',
            meta={'error': str(e), 'task_id': task_id}
        )
        
        return {
            'status': 'FAILURE',
            'error': str(e),
            'task_id': task_id
        }
    
    finally:
        db.close()


@celery_app.task(bind=True, name="batch_generate_content")
def batch_generate_content_task(
    self,
    keyword_ids: list,
    template_type: str = "default",
    include_trends: bool = True,
    include_top_posts: bool = True,
    max_posts: int = 10,
    user_id: Optional[int] = None
) -> Dict[str, Any]:
    """
    Celery task for batch content generation.
    
    Args:
        keyword_ids: List of keyword IDs to generate content for
        template_type: Template type to use
        include_trends: Whether to include trend analysis
        include_top_posts: Whether to include top posts
        max_posts: Maximum number of posts to include
        user_id: User ID for logging purposes
        
    Returns:
        Task result with batch generation information
    """
    task_id = self.request.id
    db = next(get_db())
    
    try:
        logger.info(f"Starting batch content generation task {task_id} for {len(keyword_ids)} keywords")
        
        # Create process log
        process_log = ProcessLog(
            user_id=user_id,
            task_type="batch_content_generation",
            status="running",
            task_id=task_id
        )
        db.add(process_log)
        db.commit()
        
        results = []
        total_keywords = len(keyword_ids)
        
        for i, keyword_id in enumerate(keyword_ids):
            try:
                # Update progress
                progress = int((i / total_keywords) * 100)
                self.update_state(
                    state='PROGRESS',
                    meta={
                        'progress': progress,
                        'message': f'Generating content for keyword {i+1}/{total_keywords}...',
                        'current_keyword': keyword_id
                    }
                )
                
                # Generate content for this keyword
                subtask_result = generate_blog_content_task.apply_async(
                    args=[keyword_id, template_type, include_trends, include_top_posts, max_posts, None, user_id]
                )
                
                # Wait for subtask to complete
                result = subtask_result.get(timeout=300)  # 5 minute timeout per keyword
                results.append({
                    'keyword_id': keyword_id,
                    'result': result
                })
                
            except Exception as e:
                logger.error(f"Error generating content for keyword {keyword_id}: {str(e)}")
                results.append({
                    'keyword_id': keyword_id,
                    'result': {'status': 'FAILURE', 'error': str(e)}
                })
        
        # Calculate summary
        successful = sum(1 for r in results if r['result']['status'] == 'SUCCESS')
        failed = len(results) - successful
        
        # Update process log
        process_log.status = "completed"
        process_log.completed_at = datetime.utcnow()
        db.commit()
        
        final_result = {
            'status': 'SUCCESS',
            'task_id': task_id,
            'total_keywords': total_keywords,
            'successful': successful,
            'failed': failed,
            'results': results,
            'message': f'Batch generation completed: {successful} successful, {failed} failed'
        }
        
        logger.info(f"Batch content generation task {task_id} completed")
        return final_result
        
    except Exception as e:
        logger.error(f"Error in batch content generation task {task_id}: {str(e)}")
        
        # Update process log
        try:
            process_log.status = "failed"
            process_log.error_message = str(e)
            process_log.completed_at = datetime.utcnow()
            db.commit()
        except:
            pass
        
        self.update_state(
            state='FAILURE',
            meta={'error': str(e), 'task_id': task_id}
        )
        
        return {
            'status': 'FAILURE',
            'error': str(e),
            'task_id': task_id
        }
    
    finally:
        db.close()


@celery_app.task(bind=True, name="regenerate_content")
def regenerate_content_task(
    self,
    blog_content_id: int,
    template_type: Optional[str] = None,
    custom_prompt: Optional[str] = None,
    user_id: Optional[int] = None
) -> Dict[str, Any]:
    """
    Celery task for regenerating existing blog content.
    
    Args:
        blog_content_id: ID of the blog content to regenerate
        template_type: New template type (optional)
        custom_prompt: Custom generation prompt
        user_id: User ID for logging purposes
        
    Returns:
        Task result with regenerated content information
    """
    task_id = self.request.id
    db = next(get_db())
    
    try:
        logger.info(f"Starting content regeneration task {task_id} for blog_content_id: {blog_content_id}")
        
        # Get existing blog content
        blog_content = db.query(BlogContent).filter(BlogContent.id == blog_content_id).first()
        if not blog_content:
            return {
                'status': 'FAILURE',
                'error': 'Blog content not found',
                'task_id': task_id
            }
        
        # Use existing template if not specified
        if not template_type:
            template_type = blog_content.template_used
        
        # Create process log
        process_log = ProcessLog(
            user_id=user_id,
            task_type="content_regeneration",
            status="running",
            task_id=task_id
        )
        db.add(process_log)
        db.commit()
        
        # Generate new content
        result = generate_blog_content_task.apply_async(
            args=[
                blog_content.keyword_id,
                template_type,
                True,  # include_trends
                True,  # include_top_posts
                10,    # max_posts
                custom_prompt,
                user_id
            ]
        )
        
        # Wait for generation to complete
        generation_result = result.get(timeout=300)
        
        if generation_result['status'] == 'SUCCESS':
            # Archive old content
            blog_content.status = "archived"
            db.commit()
            
            # Update process log
            process_log.status = "completed"
            process_log.completed_at = datetime.utcnow()
            db.commit()
            
            return {
                'status': 'SUCCESS',
                'task_id': task_id,
                'old_content_id': blog_content_id,
                'new_content_id': generation_result['blog_content_id'],
                'message': 'Content regenerated successfully'
            }
        else:
            # Update process log with failure
            process_log.status = "failed"
            process_log.error_message = generation_result.get('error', 'Regeneration failed')
            process_log.completed_at = datetime.utcnow()
            db.commit()
            
            return generation_result
        
    except Exception as e:
        logger.error(f"Error in content regeneration task {task_id}: {str(e)}")
        
        # Update process log
        try:
            process_log.status = "failed"
            process_log.error_message = str(e)
            process_log.completed_at = datetime.utcnow()
            db.commit()
        except:
            pass
        
        return {
            'status': 'FAILURE',
            'error': str(e),
            'task_id': task_id
        }
    
    finally:
        db.close()


@celery_app.task(name="cleanup_old_content")
def cleanup_old_content_task(days_old: int = 30) -> Dict[str, Any]:
    """
    Celery task for cleaning up old archived content.
    
    Args:
        days_old: Number of days after which to delete archived content
        
    Returns:
        Cleanup result information
    """
    db = next(get_db())
    
    try:
        logger.info(f"Starting cleanup of content older than {days_old} days")
        
        # Calculate cutoff date
        cutoff_date = datetime.utcnow() - timedelta(days=days_old)
        
        # Find old archived content
        old_content = db.query(BlogContent).filter(
            BlogContent.status == "archived",
            BlogContent.created_at < cutoff_date
        ).all()
        
        deleted_count = len(old_content)
        
        # Delete old content
        for content in old_content:
            db.delete(content)
        
        db.commit()
        
        logger.info(f"Cleaned up {deleted_count} old content items")
        
        return {
            'status': 'SUCCESS',
            'deleted_count': deleted_count,
            'cutoff_date': cutoff_date.isoformat(),
            'message': f'Cleaned up {deleted_count} old content items'
        }
        
    except Exception as e:
        logger.error(f"Error in cleanup task: {str(e)}")
        db.rollback()
        
        return {
            'status': 'FAILURE',
            'error': str(e),
            'message': 'Cleanup task failed'
        }
    
    finally:
        db.close()