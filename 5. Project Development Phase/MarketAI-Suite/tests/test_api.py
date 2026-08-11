"""
MarketAI Suite — API & Health Unit Tests
"""

import pytest
from app import create_app

@pytest.fixture
def client():
    app = create_app({
        "TESTING": True,
        "INIT_DB_FOR_TESTING": True,
        "DATABASE_PATH": ":memory:",
        "GROQ_API_KEY": "test-key",
    })
    with app.test_client() as client:
        yield client

def test_health_endpoint(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.get_json()
    assert data["success"] is True
    assert data["status"] == "healthy"
    assert "database" in data
    assert "ai_service" in data

def test_homepage(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"MarketAI" in response.data

def test_dashboard_summary_endpoint(client):
    response = client.get("/api/dashboard/summary")
    assert response.status_code == 200
    data = response.get_json()
    assert data["success"] is True
    assert "metrics" in data["data"]
