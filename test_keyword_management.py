"""
Test script for keyword management functionality.
Tests CRUD operations, duplicate validation, and user filtering.
"""

import asyncio
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.core.database import get_db, Base
from app.models.user import User
from app.models.keyword import Keyword
from app.core.security import create_access_token

# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_keywords.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

# Create test database
Base.metadata.create_all(bind=engine)

client = TestClient(app)

def setup_test_user():
    """Create a test user and return access token."""
    db = TestingSessionLocal()
    
    # Create test user
    test_user = User(
        name="Test User",
        email="test@example.com",
        oauth_provider="google"
    )
    db.add(test_user)
    db.commit()
    db.refresh(test_user)
    
    # Create access token
    access_token = create_access_token(data={"sub": str(test_user.id)})
    
    db.close()
    return access_token, test_user.id

def test_keyword_crud_operations():
    """Test complete CRUD operations for keywords."""
    print("Testing keyword CRUD operations...")
    
    # Setup
    access_token, user_id = setup_test_user()
    headers = {"Authorization": f"Bearer {access_token}"}
    
    # Test 1: Create keyword
    print("1. Testing keyword creation...")
    keyword_data = {
        "keyword": "python programming",
        "is_active": True
    }
    
    response = client.post("/api/v1/keywords/", json=keyword_data, headers=headers)
    print(f"Create response status: {response.status_code}")
    print(f"Create response: {response.json()}")
    
    assert response.status_code == 201
    created_keyword = response.json()
    assert created_keyword["keyword"] == "python programming"
    assert created_keyword["is_active"] == True
    assert created_keyword["user_id"] == user_id
    keyword_id = created_keyword["id"]
    
    # Test 2: Get keywords list
    print("\n2. Testing keyword list retrieval...")
    response = client.get("/api/v1/keywords/", headers=headers)
    print(f"List response status: {response.status_code}")
    print(f"List response: {response.json()}")
    
    assert response.status_code == 200
    keywords_list = response.json()
    assert keywords_list["total"] == 1
    assert len(keywords_list["keywords"]) == 1
    assert keywords_list["keywords"][0]["keyword"] == "python programming"
    
    # Test 3: Get specific keyword
    print("\n3. Testing specific keyword retrieval...")
    response = client.get(f"/api/v1/keywords/{keyword_id}", headers=headers)
    print(f"Get response status: {response.status_code}")
    print(f"Get response: {response.json()}")
    
    assert response.status_code == 200
    keyword = response.json()
    assert keyword["id"] == keyword_id
    assert keyword["keyword"] == "python programming"
    
    # Test 4: Update keyword
    print("\n4. Testing keyword update...")
    update_data = {
        "keyword": "machine learning",
        "is_active": False
    }
    
    response = client.put(f"/api/v1/keywords/{keyword_id}", json=update_data, headers=headers)
    print(f"Update response status: {response.status_code}")
    print(f"Update response: {response.json()}")
    
    assert response.status_code == 200
    updated_keyword = response.json()
    assert updated_keyword["keyword"] == "machine learning"
    assert updated_keyword["is_active"] == False
    
    # Test 5: Delete keyword
    print("\n5. Testing keyword deletion...")
    response = client.delete(f"/api/v1/keywords/{keyword_id}", headers=headers)
    print(f"Delete response status: {response.status_code}")
    
    assert response.status_code == 204
    
    # Verify deletion
    response = client.get(f"/api/v1/keywords/{keyword_id}", headers=headers)
    assert response.status_code == 404
    
    print("✅ All CRUD operations passed!")

def test_duplicate_validation():
    """Test keyword duplicate validation."""
    print("\nTesting duplicate validation...")
    
    # Setup
    access_token, user_id = setup_test_user()
    headers = {"Authorization": f"Bearer {access_token}"}
    
    # Create first keyword
    keyword_data = {
        "keyword": "artificial intelligence",
        "is_active": True
    }
    
    response = client.post("/api/v1/keywords/", json=keyword_data, headers=headers)
    assert response.status_code == 201
    print("First keyword created successfully")
    
    # Try to create duplicate
    response = client.post("/api/v1/keywords/", json=keyword_data, headers=headers)
    print(f"Duplicate creation response status: {response.status_code}")
    print(f"Duplicate creation response: {response.json()}")
    
    assert response.status_code == 409
    assert "already exists" in response.json()["detail"]
    
    # Test duplicate check endpoint
    response = client.post("/api/v1/keywords/check-duplicate", json=keyword_data, headers=headers)
    print(f"Duplicate check response: {response.json()}")
    
    assert response.status_code == 200
    assert response.json()["exists"] == True
    
    print("✅ Duplicate validation passed!")

def test_user_filtering():
    """Test that users can only see their own keywords."""
    print("\nTesting user filtering...")
    
    # Setup two users
    access_token1, user_id1 = setup_test_user()
    access_token2, user_id2 = setup_test_user()
    
    headers1 = {"Authorization": f"Bearer {access_token1}"}
    headers2 = {"Authorization": f"Bearer {access_token2}"}
    
    # User 1 creates a keyword
    keyword_data = {
        "keyword": "data science",
        "is_active": True
    }
    
    response = client.post("/api/v1/keywords/", json=keyword_data, headers=headers1)
    assert response.status_code == 201
    keyword_id = response.json()["id"]
    
    # User 2 should not see User 1's keyword
    response = client.get("/api/v1/keywords/", headers=headers2)
    assert response.status_code == 200
    assert response.json()["total"] == 0
    
    # User 2 should not be able to access User 1's keyword directly
    response = client.get(f"/api/v1/keywords/{keyword_id}", headers=headers2)
    assert response.status_code == 404
    
    # User 2 should not be able to update User 1's keyword
    update_data = {"keyword": "hacked"}
    response = client.put(f"/api/v1/keywords/{keyword_id}", json=update_data, headers=headers2)
    assert response.status_code == 404
    
    # User 2 should not be able to delete User 1's keyword
    response = client.delete(f"/api/v1/keywords/{keyword_id}", headers=headers2)
    assert response.status_code == 404
    
    print("✅ User filtering passed!")

def test_pagination():
    """Test keyword list pagination."""
    print("\nTesting pagination...")
    
    # Setup
    access_token, user_id = setup_test_user()
    headers = {"Authorization": f"Bearer {access_token}"}
    
    # Create multiple keywords
    keywords = ["python", "javascript", "golang", "rust", "java"]
    for keyword in keywords:
        keyword_data = {"keyword": keyword, "is_active": True}
        response = client.post("/api/v1/keywords/", json=keyword_data, headers=headers)
        assert response.status_code == 201
    
    # Test pagination
    response = client.get("/api/v1/keywords/?page=1&per_page=2", headers=headers)
    assert response.status_code == 200
    
    data = response.json()
    assert data["total"] == 5
    assert len(data["keywords"]) == 2
    assert data["page"] == 1
    assert data["per_page"] == 2
    assert data["total_pages"] == 3
    
    # Test second page
    response = client.get("/api/v1/keywords/?page=2&per_page=2", headers=headers)
    assert response.status_code == 200
    
    data = response.json()
    assert len(data["keywords"]) == 2
    assert data["page"] == 2
    
    print("✅ Pagination passed!")

def test_active_filter():
    """Test filtering by active status."""
    print("\nTesting active filter...")
    
    # Setup
    access_token, user_id = setup_test_user()
    headers = {"Authorization": f"Bearer {access_token}"}
    
    # Create active and inactive keywords
    active_keyword = {"keyword": "active_keyword", "is_active": True}
    inactive_keyword = {"keyword": "inactive_keyword", "is_active": False}
    
    client.post("/api/v1/keywords/", json=active_keyword, headers=headers)
    client.post("/api/v1/keywords/", json=inactive_keyword, headers=headers)
    
    # Test all keywords
    response = client.get("/api/v1/keywords/", headers=headers)
    assert response.json()["total"] == 2
    
    # Test active only
    response = client.get("/api/v1/keywords/?active_only=true", headers=headers)
    data = response.json()
    assert data["total"] == 1
    assert data["keywords"][0]["is_active"] == True
    
    print("✅ Active filter passed!")

if __name__ == "__main__":
    print("Starting keyword management tests...\n")
    
    try:
        test_keyword_crud_operations()
        test_duplicate_validation()
        test_user_filtering()
        test_pagination()
        test_active_filter()
        
        print("\n🎉 All tests passed successfully!")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Cleanup
        import os
        if os.path.exists("test_keywords.db"):
            os.remove("test_keywords.db")