"""
Test script to verify authentication implementation.
"""

import asyncio
import sys
import os

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.core.security import (
    create_access_token,
    create_refresh_token,
    verify_token,
    generate_oauth_state,
    verify_oauth_state,
    revoke_refresh_token
)
from app.services.auth_service import auth_service


def test_jwt_tokens():
    """Test JWT token creation and verification."""
    print("Testing JWT token functionality...")
    
    # Test access token
    user_id = 123
    access_token = create_access_token(subject=user_id)
    print(f"✓ Access token created: {access_token[:50]}...")
    
    # Verify access token
    payload = verify_token(access_token, token_type="access")
    assert payload is not None, "Access token verification failed"
    assert payload["sub"] == str(user_id), "User ID mismatch in access token"
    assert payload["type"] == "access", "Token type mismatch"
    print("✓ Access token verified successfully")
    
    # Test refresh token
    refresh_token = create_refresh_token(subject=user_id)
    print(f"✓ Refresh token created: {refresh_token[:50]}...")
    
    # Verify refresh token
    payload = verify_token(refresh_token, token_type="refresh")
    assert payload is not None, "Refresh token verification failed"
    assert payload["sub"] == str(user_id), "User ID mismatch in refresh token"
    assert payload["type"] == "refresh", "Token type mismatch"
    print("✓ Refresh token verified successfully")
    
    # Test token revocation
    success = revoke_refresh_token(refresh_token)
    assert success, "Token revocation failed"
    print("✓ Refresh token revoked successfully")
    
    # Verify revoked token fails
    payload = verify_token(refresh_token, token_type="refresh")
    assert payload is None, "Revoked token should not verify"
    print("✓ Revoked token correctly rejected")


def test_oauth_state():
    """Test OAuth state generation and verification."""
    print("\nTesting OAuth state functionality...")
    
    # Generate state
    state1 = generate_oauth_state()
    state2 = generate_oauth_state()
    print(f"✓ OAuth states generated: {state1[:20]}... and {state2[:20]}...")
    
    # Verify states are different
    assert state1 != state2, "States should be unique"
    print("✓ States are unique")
    
    # Verify state verification
    assert verify_oauth_state(state1, state1), "State verification should succeed"
    assert not verify_oauth_state(state1, state2), "Different states should not verify"
    print("✓ State verification works correctly")


def test_auth_service():
    """Test auth service functionality."""
    print("\nTesting auth service...")
    
    # Test Reddit auth URL generation
    state = "test_state_123"
    auth_url = auth_service.get_reddit_auth_url(state)
    
    assert "reddit.com" in auth_url, "Auth URL should contain reddit.com"
    assert state in auth_url, "Auth URL should contain state parameter"
    assert "client_id" in auth_url, "Auth URL should contain client_id"
    print(f"✓ Reddit auth URL generated: {auth_url[:100]}...")


def main():
    """Run all tests."""
    print("Starting authentication system tests...\n")
    
    try:
        test_jwt_tokens()
        test_oauth_state()
        test_auth_service()
        
        print("\n🎉 All authentication tests passed!")
        return True
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)