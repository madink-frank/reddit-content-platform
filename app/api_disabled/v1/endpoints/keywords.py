"""
Keyword management API endpoints.
Provides CRUD operations for user keywords with authentication.
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.keyword import (
    KeywordCreate, 
    KeywordUpdate, 
    KeywordResponse, 
    KeywordListResponse
)
from app.services.keyword_service import KeywordService


router = APIRouter()


@router.post("/", response_model=KeywordResponse, status_code=status.HTTP_201_CREATED)
async def create_keyword(
    keyword_data: KeywordCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new keyword for the authenticated user.
    
    - **keyword**: The keyword to track (required, 1-255 characters)
    - **is_active**: Whether the keyword is active for crawling (default: true)
    
    Returns the created keyword with its ID and timestamps.
    """
    keyword_service = KeywordService(db)
    keyword = await keyword_service.create_keyword(current_user.id, keyword_data)
    return keyword


@router.get("/", response_model=KeywordListResponse)
async def get_keywords(
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
    active_only: bool = Query(False, description="Filter to active keywords only"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all keywords for the authenticated user with pagination.
    
    - **page**: Page number (starts from 1)
    - **per_page**: Number of items per page (1-100)
    - **active_only**: If true, only return active keywords
    
    Returns paginated list of keywords with metadata.
    """
    keyword_service = KeywordService(db)
    skip = (page - 1) * per_page
    
    keywords, total = await keyword_service.get_user_keywords(
        current_user.id, 
        skip=skip, 
        limit=per_page,
        active_only=active_only
    )
    
    total_pages = (total + per_page - 1) // per_page
    
    return KeywordListResponse(
        keywords=keywords,
        total=total,
        page=page,
        per_page=per_page,
        total_pages=total_pages
    )


@router.get("/{keyword_id}", response_model=KeywordResponse)
async def get_keyword(
    keyword_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get a specific keyword by ID.
    
    - **keyword_id**: ID of the keyword to retrieve
    
    Returns the keyword if it exists and belongs to the authenticated user.
    """
    keyword_service = KeywordService(db)
    keyword = await keyword_service.get_keyword_by_id(keyword_id, current_user.id)
    
    if not keyword:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Keyword not found"
        )
    
    return keyword


@router.put("/{keyword_id}", response_model=KeywordResponse)
async def update_keyword(
    keyword_id: int,
    keyword_data: KeywordUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update an existing keyword.
    
    - **keyword_id**: ID of the keyword to update
    - **keyword**: New keyword text (optional)
    - **is_active**: New active status (optional)
    
    Returns the updated keyword.
    """
    keyword_service = KeywordService(db)
    keyword = await keyword_service.update_keyword(keyword_id, current_user.id, keyword_data)
    
    if not keyword:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Keyword not found"
        )
    
    return keyword


@router.delete("/{keyword_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_keyword(
    keyword_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a keyword.
    
    - **keyword_id**: ID of the keyword to delete
    
    This will also delete all associated posts and blog content.
    """
    keyword_service = KeywordService(db)
    deleted = await keyword_service.delete_keyword(keyword_id, current_user.id)
    
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Keyword not found"
        )


@router.post("/check-duplicate")
async def check_keyword_duplicate(
    keyword_data: KeywordCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Check if a keyword already exists for the user.
    
    - **keyword**: The keyword to check
    
    Returns whether the keyword already exists.
    """
    keyword_service = KeywordService(db)
    exists = await keyword_service.check_keyword_exists(current_user.id, keyword_data.keyword)
    
    return {
        "keyword": keyword_data.keyword,
        "exists": exists,
        "message": f"Keyword '{keyword_data.keyword}' {'already exists' if exists else 'is available'}"
    }