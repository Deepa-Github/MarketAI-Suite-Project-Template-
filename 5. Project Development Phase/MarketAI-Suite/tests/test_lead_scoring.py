"""
MarketAI Suite — Lead Scoring Unit Tests
"""

import io
from unittest.mock import patch
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

@patch("services.groq_service.GroqService.generate_json")
def test_score_manual_lead(mock_groq, client):
    mock_groq.return_value = {
        "lead_score": 85,
        "priority": "High",
        "lead_quality": "Excellent",
        "positive_signals": ["Demo requested"],
        "negative_signals": [],
        "score_reasoning": "High engagement",
        "recommended_action": "Schedule call",
        "recommended_channel": "Email"
    }

    payload = {
        "name": "John Smith",
        "email": "john@acme.com",
        "company": "Acme Corp",
        "demo_request": "Yes",
        "engagement_score": 80
    }

    response = client.post("/api/leads/score", json=payload)
    assert response.status_code == 201
    data = response.get_json()
    assert data["success"] is True
    assert data["data"]["lead"]["lead_score"] > 0

@patch("services.groq_service.GroqService.generate_json")
def test_upload_csv(mock_groq, client):
    mock_groq.return_value = {
        "lead_score": 75,
        "priority": "Medium",
        "score_reasoning": "Good fit"
    }

    csv_data = "name,email,company,engagement_score\nJane Doe,jane@tech.io,Tech Corp,60\n"
    data = {
        "file": (io.BytesIO(csv_data.encode("utf-8")), "leads.csv")
    }

    response = client.post("/api/leads/upload", data=data, content_type="multipart/form-data")
    assert response.status_code == 201
    res_data = response.get_json()
    assert res_data["success"] is True
    assert res_data["data"]["summary"]["total_leads"] == 1
