"""Unit tests for the email classifier service."""

import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.models.email import EmailCategory, EmailPayload, Sentiment
from src.services.classifier import EmailClassifier


@pytest.fixture
def sample_email() -> EmailPayload:
    """Create a sample email payload for testing."""
    return EmailPayload(
        message_id="test_msg_001",
        sender="customer@example.com",
        subject="Billing issue with my account",
        body="I was charged twice for my subscription last month. Please refund.",
    )


@pytest.fixture
def billing_classification_response() -> dict:
    """Mock OpenAI response for a billing email."""
    return {
        "category": "billing",
        "sentiment": "negative",
        "confidence": 0.95,
        "summary": "Customer reports duplicate charge on subscription.",
    }


@pytest.fixture
def spam_classification_response() -> dict:
    """Mock OpenAI response for a spam email."""
    return {
        "category": "spam",
        "sentiment": "neutral",
        "confidence": 0.99,
        "summary": "Unsolicited promotional email offering free prizes.",
    }


def _make_mock_response(data: dict) -> MagicMock:
    """Create a mock OpenAI chat completion response."""
    mock_message = MagicMock()
    mock_message.content = json.dumps(data)
    mock_choice = MagicMock()
    mock_choice.message = mock_message
    mock_response = MagicMock()
    mock_response.choices = [mock_choice]
    return mock_response


@pytest.mark.asyncio
async def test_classify_billing_email(
    sample_email: EmailPayload,
    billing_classification_response: dict,
) -> None:
    """Test that a billing email is correctly classified."""
    classifier = EmailClassifier(api_key="test-key")

    mock_response = _make_mock_response(billing_classification_response)

    with patch.object(
        classifier._client.chat.completions,
        "create",
        new_callable=AsyncMock,
        return_value=mock_response,
    ):
        result = await classifier.classify(sample_email)

    assert result.message_id == "test_msg_001"
    assert result.category == EmailCategory.BILLING
    assert result.sentiment == Sentiment.NEGATIVE
    assert result.confidence == 0.95
    assert "duplicate charge" in result.summary.lower()


@pytest.mark.asyncio
async def test_classify_spam_email(
    spam_classification_response: dict,
) -> None:
    """Test that spam email is correctly classified."""
    spam_email = EmailPayload(
        message_id="test_msg_002",
        sender="spam@scammer.com",
        subject="YOU WON A FREE PRIZE!!!",
        body="Click here to claim your free iPhone now!",
    )

    classifier = EmailClassifier(api_key="test-key")
    mock_response = _make_mock_response(spam_classification_response)

    with patch.object(
        classifier._client.chat.completions,
        "create",
        new_callable=AsyncMock,
        return_value=mock_response,
    ):
        result = await classifier.classify(spam_email)

    assert result.category == EmailCategory.SPAM
    assert result.confidence >= 0.9


@pytest.mark.asyncio
async def test_classify_handles_invalid_json() -> None:
    """Test that classifier raises ValueError for invalid AI response."""
    email = EmailPayload(
        message_id="test_msg_003",
        sender="test@test.com",
        subject="Test",
        body="Test body",
    )

    classifier = EmailClassifier(api_key="test-key")

    mock_message = MagicMock()
    mock_message.content = "not valid json"
    mock_choice = MagicMock()
    mock_choice.message = mock_message
    mock_response = MagicMock()
    mock_response.choices = [mock_choice]

    with patch.object(
        classifier._client.chat.completions,
        "create",
        new_callable=AsyncMock,
        return_value=mock_response,
    ):
        with pytest.raises(ValueError, match="Invalid JSON"):
            await classifier.classify(email)


@pytest.mark.asyncio
async def test_classify_handles_missing_fields() -> None:
    """Test that classifier raises ValueError when response is missing fields."""
    email = EmailPayload(
        message_id="test_msg_004",
        sender="test@test.com",
        subject="Test",
        body="Test body",
    )

    classifier = EmailClassifier(api_key="test-key")
    incomplete_response = {"category": "billing"}  # Missing other fields
    mock_response = _make_mock_response(incomplete_response)

    with patch.object(
        classifier._client.chat.completions,
        "create",
        new_callable=AsyncMock,
        return_value=mock_response,
    ):
        with pytest.raises(ValueError, match="Missing field"):
            await classifier.classify(email)


@pytest.mark.asyncio
async def test_classify_truncates_long_body() -> None:
    """Test that very long email bodies are truncated before sending to AI."""
    long_body = "A" * 5000
    email = EmailPayload(
        message_id="test_msg_005",
        sender="test@test.com",
        subject="Long email",
        body=long_body,
    )

    classifier = EmailClassifier(api_key="test-key")
    mock_data = {
        "category": "general",
        "sentiment": "neutral",
        "confidence": 0.8,
        "summary": "A very long email.",
    }
    mock_response = _make_mock_response(mock_data)

    with patch.object(
        classifier._client.chat.completions,
        "create",
        new_callable=AsyncMock,
        return_value=mock_response,
    ) as mock_create:
        await classifier.classify(email)

        call_args = mock_create.call_args
        user_message = call_args.kwargs["messages"][1]["content"]
        # Body in prompt should be truncated to 2000 chars
        assert "A" * 2000 in user_message
        assert "A" * 5000 not in user_message
