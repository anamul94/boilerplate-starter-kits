import pytest
from fastapi.testclient import TestClient

def test_root_endpoint(client: TestClient):
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "FastAPI" in data["message"]

def test_health_check(client: TestClient):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"

def test_openapi_docs(client: TestClient):
    response = client.get("/docs")
    assert response.status_code == 200

def test_openapi_json(client: TestClient):
    response = client.get("/openapi.json")
    assert response.status_code == 200
    data = response.json()
    assert "openapi" in data
    assert "info" in data

def test_cors_headers(client: TestClient):
    response = client.options("/", headers={"Origin": "http://localhost:3000"})
    assert response.status_code == 200
    assert "access-control-allow-origin" in response.headers

def test_404_error(client: TestClient):
    response = client.get("/nonexistent-endpoint")
    assert response.status_code == 404