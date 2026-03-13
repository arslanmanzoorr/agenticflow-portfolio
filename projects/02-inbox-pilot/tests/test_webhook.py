"""Integration tests for the webhook endpoint."""

import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from src.main import app
from src.models.email import ClassificationResult, EmailCategory, Sentiment


@pytest.fixture
def client() -> TestClient:
    """Create a test client for the FastAPI app."""
    return TestClient(app)


@pytest.fixture
def mock_settings() -> MagicMock:
    """Create mock settings."""
    settings = MagicMock()
    settings.openai_api_key = "test-key"
    settings.gmail_credentials_path = "./test-creds.json"
    settings.airtable_api_key = "test-airtable"
    settings.airtable_base_id = "test-base"
    return settings


def test_health_check(client: TestClient) -> None:
    """Test the health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "inbox-pilot"


def test_root_endpoint(client: TestClient) -> None:
    """Test the root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_test_classification_endpoint(client: TestClient) -> None:
    """Test the direct classification endpoint."""
    mock_result = ClassificationResult(
        message_id="test_001",
        category=EmailCategory.BILLING,
        sentiment=Sentiment.NEGATIVE,
        confidence=0.92,
        summary="Customer reports billing issue.",
    )

    with patch(
        "src.routers.webhook.get_settings"
    ) as mock_get_settings, patch(
        "src.routers.webhook.EmailClassifier"
    ) as MockClassifier:
        settings = MagicMock()
        settings.openai_api_key = "test-key"
        mock_get_settings.return_value = settings

        mock_classifier_instance = MagicMock()
        mock_classifier_instance.classify = AsyncMock(return_value=mock_result)
        MockClassifier.return_value = mock_classifier_instance

        payload = {
            "message_id": "test_001",
            "sender": "customer@example.com",
            "subject": "Billing problem",
            "body": "I was overcharged last month.",
        }

        response = client.post("/webhook/gmail/test", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert data["category"] == "billing"
    assert data["sentiment"] == "negative"
    assert data["confidence"] >= 0.9


def test_webhook_missing_data(client: TestClient) -> None:
    """Test webhook with missing message data."""
    with patch("src.routers.webhook.get_settings") as mock_get_settings:
        settings = MagicMock()
        settings.openai_api_key = "test-key"
        settings.gmail_credentials_path = "./test.json"
        mock_get_settings.return_value = settings

        payload = {"message": {}, "subscription": "test-sub"}

        response = client.post("/webhook/gmail", json=payload)
        assert response.status_code == 400


def test_stats_endpoint_empty(client: TestClient) -> None:
    """Test stats endpoint returns empty stats when no data."""
    response = client.get("/stats")
    assert response.status_code == 200
    data = response.json()
    assert data["total_processed"] >= 0


def test_recent_endpoint(client: TestClient) -> None:
    """Test recent classifications endpoint."""
    response = client.get("/stats/recent?limit=10")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_webhook_invalid_payload(client: TestClient) -> None:
    """Test webhook rejects invalid payload."""
    response = client.post("/webhook/gmail", json={"invalid": "data"})
    assert response.status_code == 422
