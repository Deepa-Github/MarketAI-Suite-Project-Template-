"""
MarketAI Suite — Campaign Unit Tests
"""

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
def test_generate_campaign(mock_groq, client):
    mock_groq.return_value = {
        "campaign_name": "SmartWatch Launch",
        "tagline": "Track your life",
        "objective": "Brand awareness",
        "value_proposition": "Best fitness tracker",
        "positioning_statement": "For professionals",
        "slogans": ["Slogan 1", "Slogan 2"],
        "promotional_content": [],
        "social_media": [],
        "email_campaign": [],
        "content_strategy": [],
        "channels": [],
        "campaign_timeline": [],
        "kpis": [],
        "optimization_recommendations": []
    }

    payload = {
        "product_name": "SmartWatch",
        "product_description": "Fitness tracking smartwatch",
        "target_audience": "Young professionals",
        "campaign_objective": "Brand Awareness"
    }

    response = client.post("/api/campaigns/generate", json=payload)
    assert response.status_code == 201
    data = response.get_json()
    assert data["success"] is True
    assert "history_id" in data["data"]
    assert data["data"]["campaign"]["campaign_name"] == "SmartWatch Launch"

def test_campaign_validation_error(client):
    response = client.post("/api/campaigns/generate", json={})
    assert response.status_code == 400
    data = response.get_json()
    assert data["success"] is False
    assert data["error"]["code"] == "VALIDATION_ERROR"
