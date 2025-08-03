"""
Unit tests for Authentication Service.
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timedelta
from jose import jwt

from app.services.auth_service import AuthService
from app.core.security import create_access_token, create_refresh_token, verify_token
from app.models.user import User
from app.schemas.auth import TokenResponse, UserResponse, LoginResponse


class TestAuthService:
    """Test cases for AuthService."""
    
    @pytest.fixture
    def auth_service(self):
        """Create AuthService instance for testing."""
        return AuthService()
    
    @pytest.mark.asyncio
    async def test_create_access_token(self, test_settings):
        """Test access token creation."""
        user_id = 1
        token = create_access_token(user_id)
        
        # Verify token structure
        assert isinstance(token, str)
        assert len(token.split('.')) == 3  # JWT has 3 parts
    
    @pytest.mark.asyncio
    async def test_create_refresh_token(self, test_settings):
        """Test refresh token creation."""
        user_id = 1
        token = create_refresh_token(user_id)
        
        # Verify token structure
        assert isinstance(token, str)
        assert len(token.split('.')) == 3
    
    @pytest.mark.asyncio
    async def test_get_reddit_auth_url(self, auth_service):
        """Test Reddit OAuth URL generation."""
        state = "test_state"
        url = auth_service.get_reddit_auth_url(state)
        
        assert isinstance(url, str)
        assert "reddit.com" in url
        assert "authorize" in url
        assert state in url
    
    @pytest.mark.asyncio
    async def test_exchange_code_for_token_success(self, auth_service):
        """Test successful code exchange."""
        code = "valid_code"
        
        with patch('httpx.AsyncClient') as mock_client:
            mock_response = MagicMock()
            mock_response.json.return_value = {
                'access_token': 'reddit_token',
                'token_type': 'bearer'
            }
            mock_response.raise_for_status = MagicMock()
            
            mock_client.return_value.__aenter__.return_value.post.return_value = mock_response
            
            result = await auth_service.exchange_code_for_token(code)
            
            assert result['access_token'] == 'reddit_token'
            assert result['token_type'] == 'bearer'
    
    @pytest.mark.asyncio
    async def test_get_reddit_user_info_success(self, auth_service):
        """Test successful user info retrieval."""
        access_token = "valid_token"
        
        with patch('httpx.AsyncClient') as mock_client:
            mock_response = MagicMock()
            mock_response.json.return_value = {
                'id': 'reddit_user_id',
                'name': 'test_user'
            }
            mock_response.raise_for_status = MagicMock()
            
            mock_client.return_value.__aenter__.return_value.get.return_value = mock_response
            
            result = await auth_service.get_reddit_user_info(access_token)
            
            assert result['id'] == 'reddit_user_id'
            assert result['name'] == 'test_user'
    
    @pytest.mark.asyncio
    async def test_authenticate_user_new_user(self, auth_service, test_db_session):
        """Test authentication with new user."""
        code = "valid_code"
        
        with patch.object(auth_service, 'exchange_code_for_token') as mock_exchange:
            mock_exchange.return_value = {'access_token': 'reddit_token'}
            
            with patch.object(auth_service, 'get_reddit_user_info') as mock_user_info:
                mock_user_info.return_value = {
                    'id': 'reddit_user_id',
                    'name': 'test_user',
                    'email': 'test@example.com'
                }
                
                # Mock database - no existing user
                test_db_session.query.return_value.filter.return_value.first.return_value = None
                test_db_session.add = MagicMock()
                test_db_session.commit = MagicMock()
                test_db_session.refresh = MagicMock()
                
                result = await auth_service.authenticate_user(code, test_db_session)
                
                assert isinstance(result, LoginResponse)
                assert result.user.name == 'test_user'
                assert result.tokens.access_token is not None
    
    @pytest.mark.asyncio
    async def test_authenticate_user_existing_user(self, auth_service, test_db_session, sample_user):
        """Test authentication with existing user."""
        code = "valid_code"
        
        with patch.object(auth_service, 'exchange_code_for_token') as mock_exchange:
            mock_exchange.return_value = {'access_token': 'reddit_token'}
            
            with patch.object(auth_service, 'get_reddit_user_info') as mock_user_info:
                mock_user_info.return_value = {
                    'id': 'reddit_user_id',
                    'name': 'updated_name',
                    'email': 'updated@example.com'
                }
                
                # Mock database - existing user
                test_db_session.query.return_value.filter.return_value.first.return_value = sample_user
                test_db_session.commit = MagicMock()
                test_db_session.refresh = MagicMock()
                
                result = await auth_service.authenticate_user(code, test_db_session)
                
                assert isinstance(result, LoginResponse)
                assert result.tokens.access_token is not None
    
    @pytest.mark.asyncio
    async def test_refresh_access_token_success(self, auth_service, test_db_session, sample_user):
        """Test successful token refresh."""
        refresh_token = create_refresh_token(sample_user.id)
        
        # Mock database query
        test_db_session.query.return_value.filter.return_value.first.return_value = sample_user
        
        with patch('app.services.auth_service.revoke_refresh_token') as mock_revoke:
            mock_revoke.return_value = True
            
            result = auth_service.refresh_access_token(refresh_token, test_db_session)
            
            assert isinstance(result, TokenResponse)
            assert result.access_token is not None
            assert result.refresh_token is not None
    
    @pytest.mark.asyncio
    async def test_logout_user_success(self, auth_service):
        """Test successful user logout."""
        refresh_token = "valid_refresh_token"
        
        with patch('app.services.auth_service.revoke_refresh_token') as mock_revoke:
            mock_revoke.return_value = True
            
            result = auth_service.logout_user(refresh_token)
            
            assert result is True
    
    @pytest.mark.asyncio
    async def test_get_current_user_success(self, auth_service, test_db_session, sample_user):
        """Test getting current user from token."""
        access_token = create_access_token(sample_user.id)
        
        # Mock database query
        test_db_session.query.return_value.filter.return_value.first.return_value = sample_user
        
        result = auth_service.get_current_user(access_token, test_db_session)
        
        assert isinstance(result, User)
        assert result.id == sample_user.id
    
    @pytest.mark.asyncio
    async def test_verify_token_valid(self, test_settings):
        """Test token verification with valid token."""
        user_id = 1
        token = create_access_token(user_id)
        
        payload = verify_token(token, token_type="access")
        
        assert isinstance(payload, dict)
        assert payload["sub"] == str(user_id)
    
    @pytest.mark.asyncio
    async def test_verify_token_invalid(self, test_settings):
        """Test token verification with invalid token."""
        invalid_token = "invalid.token.here"
        
        payload = verify_token(invalid_token, token_type="access")
        
        assert payload is None
    
    @pytest.mark.asyncio
    async def test_token_response_schema(self):
        """Test TokenResponse schema validation."""
        token_data = {
            "access_token": "test_access_token",
            "refresh_token": "test_refresh_token",
            "token_type": "bearer",
            "expires_in": 3600
        }
        
        token_response = TokenResponse(**token_data)
        
        assert token_response.access_token == "test_access_token"
        assert token_response.refresh_token == "test_refresh_token"
        assert token_response.token_type == "bearer"
        assert token_response.expires_in == 3600
    
    @pytest.mark.asyncio
    async def test_user_response_schema(self, sample_user):
        """Test UserResponse schema validation."""
        user_data = {
            "id": sample_user.id,
            "name": sample_user.name,
            "email": sample_user.email,
            "oauth_provider": sample_user.oauth_provider
        }
        
        user_response = UserResponse(**user_data)
        
        assert user_response.id == sample_user.id
        assert user_response.name == sample_user.name
        assert user_response.email == sample_user.email
    
    @pytest.mark.asyncio
    async def test_login_response_schema(self, sample_user):
        """Test LoginResponse schema validation."""
        user_response = UserResponse(
            id=sample_user.id,
            name=sample_user.name,
            email=sample_user.email,
            oauth_provider=sample_user.oauth_provider
        )
        
        token_response = TokenResponse(
            access_token="test_access",
            refresh_token="test_refresh",
            expires_in=3600
        )
        
        login_response = LoginResponse(
            user=user_response,
            tokens=token_response
        )
        
        assert login_response.user.id == sample_user.id
        assert login_response.tokens.access_token == "test_access"