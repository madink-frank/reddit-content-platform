"""
Authentication schemas for request/response validation.
"""

from typing import Optional
from pydantic import BaseModel, EmailStr


class TokenResponse(BaseModel):
    """Response schema for token endpoints."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds


class TokenRefreshRequest(BaseModel):
    """Request schema for token refresh."""
    refresh_token: str


class UserResponse(BaseModel):
    """Response schema for user information."""
    id: int
    name: str
    email: EmailStr
    oauth_provider: str
    
    class Config:
        from_attributes = True


class LoginResponse(BaseModel):
    """Response schema for successful login."""
    user: UserResponse
    tokens: TokenResponse


class AuthCallbackRequest(BaseModel):
    """Request schema for OAuth callback."""
    code: str
    state: Optional[str] = None


class LogoutResponse(BaseModel):
    """Response schema for logout."""
    message: str = "Successfully logged out"


class ErrorResponse(BaseModel):
    """Error response schema."""
    error: str
    error_description: Optional[str] = None