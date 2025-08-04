"""
Authentication endpoints for OAuth2 flow and JWT token management.
"""

from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Request, Response
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.core.dependencies import get_db, get_current_user
from app.core.security import generate_oauth_state, verify_oauth_state
from app.services.auth_service import auth_service
from app.schemas.auth import (
    TokenResponse, 
    LoginResponse, 
    TokenRefreshRequest,
    AuthCallbackRequest,
    LogoutResponse,
    ErrorResponse,
    UserResponse
)
from app.models.user import User

router = APIRouter()

# In-memory state storage (in production, use Redis)
_oauth_states: Dict[str, str] = {}


@router.get(
    "/login",
    summary="Initiate OAuth2 login",
    description="Redirect to Reddit OAuth2 authorization page to start the login process.",
    responses={
        302: {"description": "Redirect to Reddit OAuth2 authorization page"},
        500: {"description": "Internal server error"}
    }
)
async def login():
    """Initiate Reddit OAuth2 login flow."""
    try:
        # Generate secure state parameter
        state = generate_oauth_state()
        _oauth_states[state] = state  # Store state for verification
        
        # Get Reddit authorization URL
        auth_url = auth_service.get_reddit_auth_url(state)
        
        return RedirectResponse(url=auth_url, status_code=302)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to initiate login: {str(e)}"
        )


@router.get(
    "/callback",
    response_model=LoginResponse,
    summary="OAuth2 callback handler",
    description="Handle OAuth2 callback from Reddit and complete authentication process.",
    responses={
        200: {
            "description": "Successful authentication",
            "model": LoginResponse
        },
        400: {
            "description": "Invalid authorization code or state",
            "model": ErrorResponse
        },
        500: {
            "description": "Authentication failed",
            "model": ErrorResponse
        }
    }
)
async def auth_callback(
    code: str,
    state: str,
    db: Session = Depends(get_db)
):
    """Handle OAuth2 callback and complete authentication."""
    try:
        # Verify state parameter to prevent CSRF attacks
        if state not in _oauth_states:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid state parameter"
            )
        
        # Remove used state
        del _oauth_states[state]
        
        # Complete authentication
        login_response = await auth_service.authenticate_user(code, db)
        
        return login_response
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Authentication failed: {str(e)}"
        )


@router.post(
    "/refresh",
    response_model=TokenResponse,
    summary="Refresh access token",
    description="Generate a new access token using a valid refresh token.",
    responses={
        200: {
            "description": "New access token generated",
            "model": TokenResponse
        },
        401: {
            "description": "Invalid or expired refresh token",
            "model": ErrorResponse
        }
    }
)
async def refresh_token(
    token_request: TokenRefreshRequest,
    db: Session = Depends(get_db)
):
    """Refresh access token using refresh token."""
    try:
        token_response = auth_service.refresh_access_token(
            token_request.refresh_token, db
        )
        return token_response
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Token refresh failed: {str(e)}"
        )


@router.post(
    "/logout",
    response_model=LogoutResponse,
    summary="Logout user",
    description="Logout user by revoking the refresh token.",
    responses={
        200: {
            "description": "Successfully logged out",
            "model": LogoutResponse
        },
        400: {
            "description": "Invalid refresh token",
            "model": ErrorResponse
        }
    }
)
async def logout(
    token_request: TokenRefreshRequest,
    current_user: User = Depends(get_current_user)
):
    """Logout user by revoking refresh token."""
    try:
        success = auth_service.logout_user(token_request.refresh_token)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid refresh token"
            )
        
        return LogoutResponse()
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Logout failed: {str(e)}"
        )


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current user",
    description="Get information about the currently authenticated user.",
    responses={
        200: {
            "description": "Current user information",
            "model": UserResponse
        },
        401: {
            "description": "Authentication required",
            "model": ErrorResponse
        }
    }
)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """Get current authenticated user information."""
    return UserResponse.from_orm(current_user)


@router.get(
    "/status",
    summary="Check authentication status",
    description="Check if the current request is authenticated.",
    responses={
        200: {
            "description": "Authentication status",
            "content": {
                "application/json": {
                    "example": {
                        "authenticated": True,
                        "user_id": 123,
                        "username": "example_user"
                    }
                }
            }
        }
    }
)
async def auth_status(
    current_user: User = Depends(get_current_user)
):
    """Check authentication status."""
    return {
        "authenticated": True,
        "user_id": current_user.id,
        "username": current_user.name,
        "email": current_user.email,
        "provider": current_user.oauth_provider
    }