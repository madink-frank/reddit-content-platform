"""
Authentication service for OAuth2 flow and user management.
"""

from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
import httpx
import urllib.parse
from datetime import datetime, timedelta

from app.core.config import settings
from app.core.security import (
    create_access_token, 
    create_refresh_token, 
    verify_token,
    generate_oauth_state,
    verify_oauth_state,
    revoke_refresh_token
)
from app.models.user import User
from app.schemas.auth import TokenResponse, LoginResponse, UserResponse


class AuthService:
    """Service for handling OAuth2 authentication and token management."""
    
    def __init__(self):
        self.reddit_auth_url = "https://www.reddit.com/api/v1/authorize"
        self.reddit_token_url = "https://www.reddit.com/api/v1/access_token"
        self.reddit_user_url = "https://oauth.reddit.com/api/v1/me"
        
    def get_reddit_auth_url(self, state: str) -> str:
        """Generate Reddit OAuth2 authorization URL."""
        params = {
            "client_id": settings.REDDIT_CLIENT_ID,
            "response_type": "code",
            "state": state,
            "redirect_uri": settings.REDDIT_REDIRECT_URI,
            "duration": "permanent",
            "scope": "identity read"
        }
        
        return f"{self.reddit_auth_url}?{urllib.parse.urlencode(params)}"
    
    async def exchange_code_for_token(self, code: str) -> Dict[str, Any]:
        """Exchange authorization code for Reddit access token."""
        async with httpx.AsyncClient() as client:
            # Prepare token request
            auth = (settings.REDDIT_CLIENT_ID, settings.REDDIT_CLIENT_SECRET)
            headers = {
                "User-Agent": settings.REDDIT_USER_AGENT
            }
            data = {
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": settings.REDDIT_REDIRECT_URI
            }
            
            try:
                response = await client.post(
                    self.reddit_token_url,
                    auth=auth,
                    headers=headers,
                    data=data
                )
                response.raise_for_status()
                return response.json()
            except httpx.HTTPError as e:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Failed to exchange code for token: {str(e)}"
                )
    
    async def get_reddit_user_info(self, access_token: str) -> Dict[str, Any]:
        """Get user information from Reddit API."""
        async with httpx.AsyncClient() as client:
            headers = {
                "Authorization": f"Bearer {access_token}",
                "User-Agent": settings.REDDIT_USER_AGENT
            }
            
            try:
                response = await client.get(self.reddit_user_url, headers=headers)
                response.raise_for_status()
                return response.json()
            except httpx.HTTPError as e:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Failed to get user info: {str(e)}"
                )
    
    async def authenticate_user(self, code: str, db: Session) -> LoginResponse:
        """Complete OAuth2 authentication flow."""
        # Exchange code for Reddit access token
        token_data = await self.exchange_code_for_token(code)
        reddit_access_token = token_data.get("access_token")
        
        if not reddit_access_token:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to obtain access token from Reddit"
            )
        
        # Get user info from Reddit
        user_info = await self.get_reddit_user_info(reddit_access_token)
        
        # Extract user data
        reddit_id = user_info.get("id")
        name = user_info.get("name", "")
        email = user_info.get("email")  # Note: Reddit may not provide email
        
        if not reddit_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to get user ID from Reddit"
            )
        
        # Find or create user
        user = db.query(User).filter(
            User.oauth_provider == "reddit",
            User.oauth_id == reddit_id
        ).first()
        
        if not user:
            # Create new user
            user = User(
                name=name,
                email=email or f"{reddit_id}@reddit.local",  # Fallback email
                oauth_provider="reddit",
                oauth_id=reddit_id
            )
            db.add(user)
            db.commit()
            db.refresh(user)
        else:
            # Update existing user info
            user.name = name
            if email:
                user.email = email
            user.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(user)
        
        # Generate JWT tokens
        access_token = create_access_token(subject=user.id)
        refresh_token = create_refresh_token(subject=user.id)
        
        # Create response
        user_response = UserResponse.from_orm(user)
        token_response = TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )
        
        return LoginResponse(user=user_response, tokens=token_response)
    
    def refresh_access_token(self, refresh_token: str, db: Session) -> TokenResponse:
        """Generate new access token using refresh token."""
        # Verify refresh token
        payload = verify_token(refresh_token, token_type="refresh")
        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload"
            )
        
        # Verify user exists
        user = db.query(User).filter(User.id == int(user_id)).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        
        # Generate new tokens
        new_access_token = create_access_token(subject=user.id)
        new_refresh_token = create_refresh_token(subject=user.id)
        
        # Revoke old refresh token
        revoke_refresh_token(refresh_token)
        
        return TokenResponse(
            access_token=new_access_token,
            refresh_token=new_refresh_token,
            expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )
    
    def logout_user(self, refresh_token: str) -> bool:
        """Logout user by revoking refresh token."""
        return revoke_refresh_token(refresh_token)
    
    def get_current_user(self, access_token: str, db: Session) -> User:
        """Get current user from access token."""
        payload = verify_token(access_token, token_type="access")
        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid access token"
            )
        
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload"
            )
        
        user = db.query(User).filter(User.id == int(user_id)).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        
        return user


# Global auth service instance
auth_service = AuthService()