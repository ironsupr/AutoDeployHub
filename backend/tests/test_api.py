import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to AutoDeployHub API"}

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

def test_login_redirect():
    # Test that /auth/login redirects to github
    response = client.get("/auth/login", follow_redirects=False)
    assert response.status_code == 307 or response.status_code == 200 # Depending on if GITHUB_CLIENT_ID is set
