"""
Security utilities for JWT token handling and OAuth2 authentication.
"""

from datetime import datetime, timedelta
from typing import Any, Union, Optional, Dict
from jose import jwt, JWTError
from passlib.context import CryptContext
from fastapi import HTTPException, status
from app.core.config import settings
import secrets
import hashlib

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# In-memory store for refresh tokens (in production, use Redis)
_refresh_token_store: Dict[str, Dict[str, Any]] = {}


def create_access_token(
    subject: Union[str, Any], expires_delta: Optional[timedelta] = None
) -> str:
    """Create JWT access token."""
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
        )
    
    to_encode = {
        "exp": expire, 
        "sub": str(subject), 
        "type": "access",
        "iat": datetime.utcnow()
    }
    encoded_jwt = jwt.encode(
        to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM
    )
    return encoded_jwt


def create_refresh_token(
    subject: Union[str, Any], expires_delta: Optional[timedelta] = None
) -> str:
    """Create JWT refresh token and store it securely."""
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS
        )
    
    # Generate a secure random token
    token_id = secrets.token_urlsafe(32)
    
    to_encode = {
        "exp": expire, 
        "sub": str(subject), 
        "type": "refresh",
        "jti": token_id,  # JWT ID for token revocation
        "iat": datetime.utcnow()
    }
    encoded_jwt = jwt.encode(
        to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM
    )
    
    # Store refresh token metadata for revocation
    _refresh_token_store[token_id] = {
        "user_id": str(subject),
        "created_at": datetime.utcnow(),
        "expires_at": expire,
        "revoked": False
    }
    
    return encoded_jwt


def verify_token(token: str, token_type: str = "access") -> Optional[Dict[str, Any]]:
    """Verify JWT token and return payload."""
    try:
        payload = jwt.decode(
            token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
        )
        
        # Check token type
        if payload.get("type") != token_type:
            return None
            
        # For refresh tokens, check if revoked
        if token_type == "refresh":
            token_id = payload.get("jti")
            if token_id and token_id in _refresh_token_store:
                if _refresh_token_store[token_id]["revoked"]:
                    return None
        
        return payload
    except JWTError:
        return None


def revoke_refresh_token(token: str) -> bool:
    """Revoke a refresh token."""
    try:
        payload = jwt.decode(
            token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
        )
        token_id = payload.get("jti")
        if token_id and token_id in _refresh_token_store:
            _refresh_token_store[token_id]["revoked"] = True
            return True
        return False
    except JWTError:
        return False


def generate_oauth_state() -> str:
    """Generate a secure state parameter for OAuth2 flow."""
    return secrets.token_urlsafe(32)


def verify_oauth_state(state: str, stored_state: str) -> bool:
    """Verify OAuth2 state parameter to prevent CSRF attacks."""
    return secrets.compare_digest(state, stored_state)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Generate password hash."""
    return pwd_context.hash(password)