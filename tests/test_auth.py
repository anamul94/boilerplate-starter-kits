import pytest
from fastapi.testclient import TestClient

def test_login_success(client: TestClient, test_user_data, db):
    # Create user first
    response = client.post("/api/users/", json=test_user_data)
    assert response.status_code == 201
    
    # Test login
    login_data = {
        "username": test_user_data["email"],
        "password": test_user_data["password"]
    }
    response = client.post("/api/auth/login", data=login_data)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_invalid_credentials(client: TestClient):
    login_data = {
        "username": "nonexistent@example.com",
        "password": "wrongpassword"
    }
    response = client.post("/api/auth/login", data=login_data)
    assert response.status_code == 401
    assert "Incorrect username or password" in response.json()["detail"]

def test_google_login_redirect(client: TestClient):
    response = client.get("/api/auth/google-login", allow_redirects=False)
    assert response.status_code == 307  # Redirect status

def test_rate_limiting(client: TestClient):
    login_data = {
        "username": "test@example.com",
        "password": "wrongpassword"
    }
    
    # Make multiple requests to trigger rate limit
    for _ in range(6):  # Exceed the limit of 5
        response = client.post("/api/auth/login", data=login_data)
    
    # Last request should be rate limited
    assert response.status_code == 429
    assert "Too many authentication attempts" in response.json()["detail"]