"""
Unit tests for Keyword Service.
"""
import pytest
from unittest.mock import MagicMock, AsyncMock
from sqlalchemy.exc import IntegrityError

from app.services.keyword_service import KeywordService
from app.models.keyword import Keyword
from app.schemas.keyword import KeywordCreate, KeywordUpdate


class TestKeywordService:
    """Test cases for KeywordService."""
    
    @pytest.fixture
    def keyword_service(self, test_db_session):
        """Create KeywordService instance for testing."""
        return KeywordService(db=test_db_session)
    
    @pytest.mark.asyncio
    async def test_create_keyword_success(self, keyword_service, sample_user):
        """Test successful keyword creation."""
        keyword_data = KeywordCreate(keyword="python programming")
        
        # Mock database operations
        keyword_service.db.query.return_value.filter.return_value.first.return_value = None
        keyword_service.db.add = MagicMock()
        keyword_service.db.commit = MagicMock()
        keyword_service.db.refresh = MagicMock()
        
        # Mock the created keyword
        created_keyword = Keyword(
            id=1,
            user_id=sample_user.id,
            keyword=keyword_data.keyword,
            is_active=True
        )
        keyword_service.db.refresh.side_effect = lambda obj: setattr(obj, 'id', 1)
        
        result = await keyword_service.create_keyword(sample_user.id, keyword_data)
        
        assert isinstance(result, Keyword)
        assert result.keyword == keyword_data.keyword
        assert result.user_id == sample_user.id
        assert result.is_active is True
        
        keyword_service.db.add.assert_called_once()
        keyword_service.db.commit.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_create_keyword_duplicate(self, keyword_service, sample_user, sample_keyword):
        """Test creating duplicate keyword."""
        keyword_data = KeywordCreate(keyword=sample_keyword.keyword)
        
        # Mock existing keyword found
        keyword_service.db.query.return_value.filter.return_value.first.return_value = sample_keyword
        
        with pytest.raises(ValueError, match="Keyword already exists"):
            await keyword_service.create_keyword(sample_user.id, keyword_data)
    
    @pytest.mark.asyncio
    async def test_create_keyword_empty_string(self, keyword_service, sample_user):
        """Test creating keyword with empty string."""
        keyword_data = KeywordCreate(keyword="")
        
        with pytest.raises(ValueError, match="Keyword cannot be empty"):
            await keyword_service.create_keyword(sample_user.id, keyword_data)
    
    @pytest.mark.asyncio
    async def test_create_keyword_whitespace_only(self, keyword_service, sample_user):
        """Test creating keyword with whitespace only."""
        keyword_data = KeywordCreate(keyword="   ")
        
        with pytest.raises(ValueError, match="Keyword cannot be empty"):
            await keyword_service.create_keyword(sample_user.id, keyword_data)
    
    @pytest.mark.asyncio
    async def test_get_user_keywords_success(self, keyword_service, sample_user):
        """Test retrieving user keywords."""
        keywords = [
            Keyword(id=1, user_id=sample_user.id, keyword="python", is_active=True),
            Keyword(id=2, user_id=sample_user.id, keyword="javascript", is_active=True),
            Keyword(id=3, user_id=sample_user.id, keyword="rust", is_active=False)
        ]
        
        # Mock database query
        keyword_service.db.query.return_value.filter.return_value.all.return_value = keywords
        
        result = await keyword_service.get_user_keywords(sample_user.id)
        
        assert len(result) == 3
        assert all(isinstance(k, Keyword) for k in result)
        assert all(k.user_id == sample_user.id for k in result)
    
    @pytest.mark.asyncio
    async def test_get_user_keywords_active_only(self, keyword_service, sample_user):
        """Test retrieving only active user keywords."""
        active_keywords = [
            Keyword(id=1, user_id=sample_user.id, keyword="python", is_active=True),
            Keyword(id=2, user_id=sample_user.id, keyword="javascript", is_active=True)
        ]
        
        # Mock database query with active filter
        keyword_service.db.query.return_value.filter.return_value.filter.return_value.all.return_value = active_keywords
        
        result = await keyword_service.get_user_keywords(sample_user.id, active_only=True)
        
        assert len(result) == 2
        assert all(k.is_active for k in result)
    
    @pytest.mark.asyncio
    async def test_get_user_keywords_empty(self, keyword_service, sample_user):
        """Test retrieving keywords when user has none."""
        # Mock empty result
        keyword_service.db.query.return_value.filter.return_value.all.return_value = []
        
        result = await keyword_service.get_user_keywords(sample_user.id)
        
        assert result == []
    
    @pytest.mark.asyncio
    async def test_get_keyword_by_id_success(self, keyword_service, sample_keyword):
        """Test retrieving keyword by ID."""
        # Mock database query
        keyword_service.db.query.return_value.filter.return_value.first.return_value = sample_keyword
        
        result = await keyword_service.get_keyword_by_id(sample_keyword.id)
        
        assert result == sample_keyword
    
    @pytest.mark.asyncio
    async def test_get_keyword_by_id_not_found(self, keyword_service):
        """Test retrieving non-existent keyword."""
        # Mock database query returning None
        keyword_service.db.query.return_value.filter.return_value.first.return_value = None
        
        result = await keyword_service.get_keyword_by_id(999)
        
        assert result is None
    
    @pytest.mark.asyncio
    async def test_update_keyword_success(self, keyword_service, sample_keyword):
        """Test successful keyword update."""
        update_data = KeywordUpdate(keyword="updated python")
        
        # Mock database operations
        keyword_service.db.query.return_value.filter.return_value.first.return_value = sample_keyword
        keyword_service.db.commit = MagicMock()
        keyword_service.db.refresh = MagicMock()
        
        result = await keyword_service.update_keyword(sample_keyword.id, update_data)
        
        assert isinstance(result, Keyword)
        assert result.keyword == update_data.keyword
        keyword_service.db.commit.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_update_keyword_not_found(self, keyword_service):
        """Test updating non-existent keyword."""
        update_data = KeywordUpdate(keyword="updated keyword")
        
        # Mock database query returning None
        keyword_service.db.query.return_value.filter.return_value.first.return_value = None
        
        with pytest.raises(ValueError, match="Keyword not found"):
            await keyword_service.update_keyword(999, update_data)
    
    @pytest.mark.asyncio
    async def test_update_keyword_duplicate(self, keyword_service, sample_keyword):
        """Test updating keyword to duplicate value."""
        update_data = KeywordUpdate(keyword="existing keyword")
        
        # Mock finding the keyword to update
        keyword_service.db.query.return_value.filter.return_value.first.return_value = sample_keyword
        
        # Mock commit raising IntegrityError
        keyword_service.db.commit.side_effect = IntegrityError("", "", "")
        
        with pytest.raises(ValueError, match="Keyword already exists"):
            await keyword_service.update_keyword(sample_keyword.id, update_data)
    
    @pytest.mark.asyncio
    async def test_delete_keyword_success(self, keyword_service, sample_keyword):
        """Test successful keyword deletion."""
        # Mock database operations
        keyword_service.db.query.return_value.filter.return_value.first.return_value = sample_keyword
        keyword_service.db.delete = MagicMock()
        keyword_service.db.commit = MagicMock()
        
        result = await keyword_service.delete_keyword(sample_keyword.id)
        
        assert result is True
        keyword_service.db.delete.assert_called_once_with(sample_keyword)
        keyword_service.db.commit.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_delete_keyword_not_found(self, keyword_service):
        """Test deleting non-existent keyword."""
        # Mock database query returning None
        keyword_service.db.query.return_value.filter.return_value.first.return_value = None
        
        with pytest.raises(ValueError, match="Keyword not found"):
            await keyword_service.delete_keyword(999)
    
    @pytest.mark.asyncio
    async def test_toggle_keyword_status_activate(self, keyword_service, sample_keyword):
        """Test activating inactive keyword."""
        sample_keyword.is_active = False
        
        # Mock database operations
        keyword_service.db.query.return_value.filter.return_value.first.return_value = sample_keyword
        keyword_service.db.commit = MagicMock()
        keyword_service.db.refresh = MagicMock()
        
        result = await keyword_service.toggle_keyword_status(sample_keyword.id)
        
        assert result.is_active is True
        keyword_service.db.commit.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_toggle_keyword_status_deactivate(self, keyword_service, sample_keyword):
        """Test deactivating active keyword."""
        sample_keyword.is_active = True
        
        # Mock database operations
        keyword_service.db.query.return_value.filter.return_value.first.return_value = sample_keyword
        keyword_service.db.commit = MagicMock()
        keyword_service.db.refresh = MagicMock()
        
        result = await keyword_service.toggle_keyword_status(sample_keyword.id)
        
        assert result.is_active is False
        keyword_service.db.commit.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_search_keywords_success(self, keyword_service, sample_user):
        """Test keyword search functionality."""
        keywords = [
            Keyword(id=1, user_id=sample_user.id, keyword="python programming", is_active=True),
            Keyword(id=2, user_id=sample_user.id, keyword="python web", is_active=True)
        ]
        
        # Mock database query with search
        keyword_service.db.query.return_value.filter.return_value.filter.return_value.all.return_value = keywords
        
        result = await keyword_service.search_keywords(sample_user.id, "python")
        
        assert len(result) == 2
        assert all("python" in k.keyword.lower() for k in result)
    
    @pytest.mark.asyncio
    async def test_get_keyword_statistics(self, keyword_service, sample_user):
        """Test getting keyword statistics."""
        # Mock database queries for statistics
        keyword_service.db.query.return_value.filter.return_value.count.return_value = 5  # total
        keyword_service.db.query.return_value.filter.return_value.filter.return_value.count.return_value = 3  # active
        
        result = await keyword_service.get_keyword_statistics(sample_user.id)
        
        assert result["total_keywords"] == 5
        assert result["active_keywords"] == 3
        assert result["inactive_keywords"] == 2
    
    @pytest.mark.asyncio
    async def test_validate_keyword_format_valid(self, keyword_service):
        """Test keyword format validation with valid input."""
        valid_keywords = [
            "python",
            "machine learning",
            "web-development",
            "AI/ML",
            "C++",
            "Node.js"
        ]
        
        for keyword in valid_keywords:
            result = keyword_service.validate_keyword_format(keyword)
            assert result is True
    
    @pytest.mark.asyncio
    async def test_validate_keyword_format_invalid(self, keyword_service):
        """Test keyword format validation with invalid input."""
        invalid_keywords = [
            "",  # empty
            "   ",  # whitespace only
            "a" * 101,  # too long
            "keyword with @#$%",  # special characters
        ]
        
        for keyword in invalid_keywords:
            result = keyword_service.validate_keyword_format(keyword)
            assert result is False