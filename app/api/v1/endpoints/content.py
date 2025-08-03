"""
Content management API endpoints.
"""

import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.blog_content import BlogContent
from app.models.keyword import Keyword
from app.schemas.blog_content import (
    BlogContentResponse,
    BlogContentListResponse,
    BlogContentCreate,
    BlogContentUpdate,
    ContentGenerationRequest,
    ContentGenerationResponse,
    ContentGenerationStatus,
    TemplateListResponse,
    ContentPreview
)
from app.services.content_generation_service import ContentGenerationService
from app.services.template_service import TemplateService
from app.workers.content_tasks import (
    generate_blog_content_task,
    batch_generate_content_task,
    regenerate_content_task
)
from app.services.task_service import TaskService

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/generate", response_model=ContentGenerationResponse)
async def generate_content(
    request: ContentGenerationRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Generate blog content for a keyword.
    """
    try:
        # Verify keyword belongs to user
        keyword = db.query(Keyword).filter(
            and_(Keyword.id == request.keyword_id, Keyword.user_id == current_user.id)
        ).first()
        
        if not keyword:
            raise HTTPException(status_code=404, detail="Keyword not found")
        
        # Start content generation task
        task = generate_blog_content_task.delay(
            keyword_id=request.keyword_id,
            template_type=request.template_type,
            include_trends=request.include_trends,
            include_top_posts=request.include_top_posts,
            max_posts=request.max_posts,
            custom_prompt=request.custom_prompt,
            user_id=current_user.id
        )
        
        logger.info(f"Started content generation task {task.id} for user {current_user.id}")
        
        return ContentGenerationResponse(
            task_id=task.id,
            status="pending",
            message="Content generation started"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error starting content generation: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to start content generation")


@router.post("/batch-generate", response_model=ContentGenerationResponse)
async def batch_generate_content(
    keyword_ids: List[int],
    template_type: str = "default",
    include_trends: bool = True,
    include_top_posts: bool = True,
    max_posts: int = 10,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Generate blog content for multiple keywords.
    """
    try:
        # Verify all keywords belong to user
        keywords = db.query(Keyword).filter(
            and_(Keyword.id.in_(keyword_ids), Keyword.user_id == current_user.id)
        ).all()
        
        if len(keywords) != len(keyword_ids):
            raise HTTPException(status_code=404, detail="One or more keywords not found")
        
        # Start batch generation task
        task = batch_generate_content_task.delay(
            keyword_ids=keyword_ids,
            template_type=template_type,
            include_trends=include_trends,
            include_top_posts=include_top_posts,
            max_posts=max_posts,
            user_id=current_user.id
        )
        
        logger.info(f"Started batch content generation task {task.id} for user {current_user.id}")
        
        return ContentGenerationResponse(
            task_id=task.id,
            status="pending",
            message=f"Batch content generation started for {len(keyword_ids)} keywords"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error starting batch content generation: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to start batch content generation")


@router.get("/generation-status/{task_id}", response_model=ContentGenerationStatus)
async def get_generation_status(
    task_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Get content generation task status.
    """
    try:
        task_service = TaskService()
        status = await task_service.get_task_status(task_id)
        
        if not status:
            raise HTTPException(status_code=404, detail="Task not found")
        
        return ContentGenerationStatus(
            task_id=task_id,
            status=status.get("status", "unknown"),
            progress=status.get("progress", 0),
            message=status.get("message", ""),
            result=status.get("result"),
            error=status.get("error"),
            created_at=status.get("created_at"),
            completed_at=status.get("completed_at")
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting task status: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get task status")


@router.post("/preview", response_model=ContentPreview)
async def preview_content(
    request: ContentGenerationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Generate a preview of content without saving.
    """
    try:
        # Verify keyword belongs to user
        keyword = db.query(Keyword).filter(
            and_(Keyword.id == request.keyword_id, Keyword.user_id == current_user.id)
        ).first()
        
        if not keyword:
            raise HTTPException(status_code=404, detail="Keyword not found")
        
        # Generate preview
        content_service = ContentGenerationService()
        preview = content_service.preview_content(request, db)
        
        if not preview:
            raise HTTPException(status_code=500, detail="Failed to generate preview")
        
        return ContentPreview(**preview)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating content preview: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to generate preview")


@router.get("/", response_model=BlogContentListResponse)
async def list_content(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    keyword_id: Optional[int] = Query(None),
    status: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List blog content for the current user.
    """
    try:
        # Build query
        query = db.query(BlogContent).join(Keyword).filter(Keyword.user_id == current_user.id)
        
        # Apply filters
        if keyword_id:
            query = query.filter(BlogContent.keyword_id == keyword_id)
        
        if status:
            query = query.filter(BlogContent.status == status)
        
        # Get total count
        total = query.count()
        
        # Apply pagination and ordering
        content_items = query.order_by(desc(BlogContent.created_at)).offset(
            (page - 1) * size
        ).limit(size).all()
        
        # Calculate pagination info
        pages = (total + size - 1) // size
        
        return BlogContentListResponse(
            items=[BlogContentResponse.from_orm(item) for item in content_items],
            total=total,
            page=page,
            size=size,
            pages=pages
        )
        
    except Exception as e:
        logger.error(f"Error listing content: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to list content")


@router.get("/{content_id}", response_model=BlogContentResponse)
async def get_content(
    content_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get specific blog content.
    """
    try:
        content = db.query(BlogContent).join(Keyword).filter(
            and_(
                BlogContent.id == content_id,
                Keyword.user_id == current_user.id
            )
        ).first()
        
        if not content:
            raise HTTPException(status_code=404, detail="Content not found")
        
        return BlogContentResponse.from_orm(content)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting content: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get content")


@router.put("/{content_id}", response_model=BlogContentResponse)
async def update_content(
    content_id: int,
    update_data: BlogContentUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update blog content.
    """
    try:
        content = db.query(BlogContent).join(Keyword).filter(
            and_(
                BlogContent.id == content_id,
                Keyword.user_id == current_user.id
            )
        ).first()
        
        if not content:
            raise HTTPException(status_code=404, detail="Content not found")
        
        # Update fields
        update_dict = update_data.dict(exclude_unset=True)
        
        for field, value in update_dict.items():
            if field == "tags" and value:
                # Convert tags list to comma-separated string
                setattr(content, field, ",".join(value))
            else:
                setattr(content, field, value)
        
        # Update word count if content changed
        if "content" in update_dict:
            content_service = ContentGenerationService()
            content.word_count = content_service._count_words(content.content)
        
        db.commit()
        db.refresh(content)
        
        return BlogContentResponse.from_orm(content)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating content: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to update content")


@router.delete("/{content_id}")
async def delete_content(
    content_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete blog content.
    """
    try:
        content = db.query(BlogContent).join(Keyword).filter(
            and_(
                BlogContent.id == content_id,
                Keyword.user_id == current_user.id
            )
        ).first()
        
        if not content:
            raise HTTPException(status_code=404, detail="Content not found")
        
        db.delete(content)
        db.commit()
        
        return {"message": "Content deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting content: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to delete content")


@router.post("/{content_id}/regenerate", response_model=ContentGenerationResponse)
async def regenerate_content(
    content_id: int,
    template_type: Optional[str] = None,
    custom_prompt: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Regenerate existing blog content.
    """
    try:
        content = db.query(BlogContent).join(Keyword).filter(
            and_(
                BlogContent.id == content_id,
                Keyword.user_id == current_user.id
            )
        ).first()
        
        if not content:
            raise HTTPException(status_code=404, detail="Content not found")
        
        # Start regeneration task
        task = regenerate_content_task.delay(
            blog_content_id=content_id,
            template_type=template_type,
            custom_prompt=custom_prompt,
            user_id=current_user.id
        )
        
        logger.info(f"Started content regeneration task {task.id} for user {current_user.id}")
        
        return ContentGenerationResponse(
            task_id=task.id,
            status="pending",
            message="Content regeneration started"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error starting content regeneration: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to start content regeneration")


@router.get("/templates/", response_model=TemplateListResponse)
async def list_templates():
    """
    List available content templates.
    """
    try:
        template_service = TemplateService()
        templates = template_service.get_available_templates()
        
        return TemplateListResponse(
            templates=[
                {
                    "name": t["name"],
                    "description": t["description"],
                    "variables": t["variables"]
                }
                for t in templates
            ]
        )
        
    except Exception as e:
        logger.error(f"Error listing templates: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to list templates")