"""
Keyword management service.
Handles CRUD operations for user keywords with duplicate validation.
"""

from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import and_
from fastapi import HTTPException, status

from app.models.keyword import Keyword
from app.schemas.keyword import KeywordCreate, KeywordUpdate
from app.core.database import get_db


class KeywordService:
    """Service class for keyword management operations."""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def create_keyword(self, user_id: int, keyword_data: KeywordCreate) -> Keyword:
        """
        Create a new keyword for a user.
        
        Args:
            user_id: ID of the user creating the keyword
            keyword_data: Keyword creation data
            
        Returns:
            Created keyword instance
            
        Raises:
            HTTPException: If keyword already exists for the user
        """
        # Check for duplicate keyword for this user
        existing_keyword = self.db.query(Keyword).filter(
            and_(
                Keyword.user_id == user_id,
                Keyword.keyword == keyword_data.keyword
            )
        ).first()
        
        if existing_keyword:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Keyword '{keyword_data.keyword}' already exists for this user"
            )
        
        # Create new keyword
        db_keyword = Keyword(
            user_id=user_id,
            keyword=keyword_data.keyword,
            is_active=keyword_data.is_active
        )
        
        try:
            self.db.add(db_keyword)
            self.db.commit()
            self.db.refresh(db_keyword)
            return db_keyword
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Keyword '{keyword_data.keyword}' already exists for this user"
            )
    
    async def get_user_keywords(
        self, 
        user_id: int, 
        skip: int = 0, 
        limit: int = 100,
        active_only: bool = False
    ) -> tuple[List[Keyword], int]:
        """
        Get all keywords for a user with pagination.
        
        Args:
            user_id: ID of the user
            skip: Number of records to skip
            limit: Maximum number of records to return
            active_only: If True, only return active keywords
            
        Returns:
            Tuple of (keywords list, total count)
        """
        query = self.db.query(Keyword).filter(Keyword.user_id == user_id)
        
        if active_only:
            query = query.filter(Keyword.is_active == True)
        
        # Get total count
        total = query.count()
        
        # Get paginated results
        keywords = query.offset(skip).limit(limit).all()
        
        return keywords, total
    
    async def get_keyword_by_id(self, keyword_id: int, user_id: int) -> Optional[Keyword]:
        """
        Get a specific keyword by ID, ensuring it belongs to the user.
        
        Args:
            keyword_id: ID of the keyword
            user_id: ID of the user (for authorization)
            
        Returns:
            Keyword instance if found and belongs to user, None otherwise
        """
        return self.db.query(Keyword).filter(
            and_(
                Keyword.id == keyword_id,
                Keyword.user_id == user_id
            )
        ).first()
    
    async def update_keyword(
        self, 
        keyword_id: int, 
        user_id: int, 
        keyword_data: KeywordUpdate
    ) -> Optional[Keyword]:
        """
        Update an existing keyword.
        
        Args:
            keyword_id: ID of the keyword to update
            user_id: ID of the user (for authorization)
            keyword_data: Updated keyword data
            
        Returns:
            Updated keyword instance if successful, None if not found
            
        Raises:
            HTTPException: If keyword already exists for the user
        """
        # Get existing keyword
        db_keyword = await self.get_keyword_by_id(keyword_id, user_id)
        if not db_keyword:
            return None
        
        # Check for duplicate if keyword text is being updated
        if keyword_data.keyword and keyword_data.keyword != db_keyword.keyword:
            existing_keyword = self.db.query(Keyword).filter(
                and_(
                    Keyword.user_id == user_id,
                    Keyword.keyword == keyword_data.keyword,
                    Keyword.id != keyword_id  # Exclude current keyword
                )
            ).first()
            
            if existing_keyword:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Keyword '{keyword_data.keyword}' already exists for this user"
                )
        
        # Update fields
        update_data = keyword_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_keyword, field, value)
        
        try:
            self.db.commit()
            self.db.refresh(db_keyword)
            return db_keyword
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Keyword '{keyword_data.keyword}' already exists for this user"
            )
    
    async def delete_keyword(self, keyword_id: int, user_id: int) -> bool:
        """
        Delete a keyword.
        
        Args:
            keyword_id: ID of the keyword to delete
            user_id: ID of the user (for authorization)
            
        Returns:
            True if deleted successfully, False if not found
        """
        db_keyword = await self.get_keyword_by_id(keyword_id, user_id)
        if not db_keyword:
            return False
        
        self.db.delete(db_keyword)
        self.db.commit()
        return True
    
    async def check_keyword_exists(self, user_id: int, keyword: str) -> bool:
        """
        Check if a keyword already exists for a user.
        
        Args:
            user_id: ID of the user
            keyword: Keyword to check
            
        Returns:
            True if keyword exists, False otherwise
        """
        existing_keyword = self.db.query(Keyword).filter(
            and_(
                Keyword.user_id == user_id,
                Keyword.keyword == keyword.strip().lower()
            )
        ).first()
        
        return existing_keyword is not None


def get_keyword_service(db: Session = None) -> KeywordService:
    """
    Dependency function to get keyword service instance.
    
    Args:
        db: Database session
        
    Returns:
        KeywordService instance
    """
    if db is None:
        db = next(get_db())
    return KeywordService(db)