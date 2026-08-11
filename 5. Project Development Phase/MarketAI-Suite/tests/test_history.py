"""
MarketAI Suite — History Retrieval Unit Tests
Verifies that retrieving a previously generated result reads from DB
and NEVER calls the Groq AI API.
"""

from unittest.mock import patch
import pytest
from app import create_app
from models.schemas import HistoryRepository

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

@patch("services.groq_service.GroqService.generate")
@patch("services.groq_service.GroqService.generate_json")
def test_history_retrieval_does_not_call_groq(mock_groq_json, mock_groq_gen, client):
    # 1. Create a dummy history record directly in DB
    record = HistoryRepository.create(
        generation_type="campaign",
        title="Campaign: SmartWatch",
        user_inputs={"product_name": "SmartWatch"},
        ai_output={"campaign_name": "SmartWatch Campaign", "slogans": ["Slogan 1"]}
    )

    record_id = record["id"]

    # 2. Retrieve history item via API
    response = client.get(f"/api/history/{record_id}")
    assert response.status_code == 200
    data = response.get_json()

    assert data["success"] is True
    assert data["data"]["ai_output"]["campaign_name"] == "SmartWatch Campaign"
    assert data["data"]["loaded_from_history"] is True

    # 3. VERIFY: Neither Groq generate nor generate_json was called
    mock_groq_gen.assert_not_called()
    mock_groq_json.assert_not_called()
