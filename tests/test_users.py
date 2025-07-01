import pytest
from fastapi.testclient import TestClient

def test_create_user_success(client: TestClient, test_user_data, db):
    response = client.post("/api/users/", json=test_user_data)
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == test_user_data["email"]
    assert data["username"] == test_user_data["username"]
    assert "id" in data

def test_create_user_invalid_password(client: TestClient, db):
    user_data = {
        "email": "test@example.com",
        "username": "testuser",
        "password": "weak"  # Too short
    }
    response = client.post("/api/users/", json=user_data)
    assert response.status_code == 422
    data = response.json()
    assert "Validation failed" in data["error"]

def test_create_user_invalid_email(client: TestClient, db):
    user_data = {
        "email": "invalid-email",
        "username": "testuser",
        "password": "TestPass123"
    }
    response = client.post("/api/users/", json=user_data)
    assert response.status_code == 422

def test_create_user_duplicate_email(client: TestClient, test_user_data, db):
    # Create first user
    response = client.post("/api/users/", json=test_user_data)
    assert response.status_code == 201
    
    # Try to create user with same email
    response = client.post("/api/users/", json=test_user_data)
    assert response.status_code == 400

def test_get_current_user(client: TestClient, test_user_data, db):
    # Create and login user
    client.post("/api/users/", json=test_user_data)
    login_response = client.post("/api/auth/login", data={
        "username": test_user_data["email"],
        "password": test_user_data["password"]
    })
    token = login_response.json()["access_token"]
    
    # Get current user
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/api/users/me", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == test_user_data["email"]

def test_get_current_user_unauthorized(client: TestClient):
    response = client.get("/api/users/me")
    assert response.status_code == 401