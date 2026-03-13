"""Tests for the ActionExtractorService."""

import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.models.meeting import ActionItem, Priority
from src.services.action_extractor import ActionExtractionError, ActionExtractorService


SAMPLE_TRANSCRIPT = (
    "Alice: We need to update the landing page copy by end of week. "
    "Bob, can you handle that?\n"
    "Bob: Sure, I'll get it done by Friday.\n"
    "Alice: Charlie, please review the analytics dashboard. There might "
    "be a bug in the conversion tracking. This is urgent.\n"
    "Charlie: I'll look into it today.\n"
    "Alice: Also, we should schedule a follow-up meeting next Tuesday "
    "to review progress. I'll send the invite.\n"
    "Bob: Sounds good. I'll also prepare the A/B test results for that meeting."
)

MOCK_GPT_RESPONSE = {
    "action_items": [
        {
            "description": "Update the landing page copy",
            "assigned_to": "Bob",
            "deadline": "Friday",
            "priority": "medium",
        },
        {
            "description": "Review analytics dashboard for conversion tracking bug",
            "assigned_to": "Charlie",
            "deadline": "Today",
            "priority": "high",
        },
        {
            "description": "Schedule follow-up meeting for next Tuesday",
            "assigned_to": "Alice",
            "deadline": "Next Tuesday",
            "priority": "medium",
        },
        {
            "description": "Prepare A/B test results for follow-up meeting",
            "assigned_to": "Bob",
            "deadline": "Next Tuesday",
            "priority": "low",
        },
    ]
}


def _make_mock_response(content: str) -> MagicMock:
    """Build a mock OpenAI chat completion response."""
    message = MagicMock()
    message.content = content
    choice = MagicMock()
    choice.message = message
    response = MagicMock()
    response.choices = [choice]
    return response


@pytest.fixture
def mock_settings():
    """Patch get_settings to return test configuration."""
    with patch("src.services.action_extractor.get_settings") as mock:
        settings = MagicMock()
        settings.openai_api_key = "sk-test-key"
        settings.openai_model = "gpt-4"
        mock.return_value = settings
        yield settings


@pytest.fixture
def extractor(mock_settings):
    """Create an ActionExtractorService with mocked settings."""
    with patch("src.services.action_extractor.AsyncOpenAI") as mock_client_cls:
        service = ActionExtractorService()
        service._client = mock_client_cls.return_value
        yield service


@pytest.mark.asyncio
async def test_extract_returns_action_items(extractor):
    """Test that extract() returns a list of ActionItem objects."""
    mock_resp = _make_mock_response(json.dumps(MOCK_GPT_RESPONSE))
    extractor._client.chat.completions.create = AsyncMock(return_value=mock_resp)

    result = await extractor.extract(SAMPLE_TRANSCRIPT)

    assert isinstance(result, list)
    assert len(result) == 4
    assert all(isinstance(item, ActionItem) for item in result)


@pytest.mark.asyncio
async def test_extract_parses_descriptions(extractor):
    """Test that action item descriptions are correctly parsed."""
    mock_resp = _make_mock_response(json.dumps(MOCK_GPT_RESPONSE))
    extractor._client.chat.completions.create = AsyncMock(return_value=mock_resp)

    result = await extractor.extract(SAMPLE_TRANSCRIPT)

    descriptions = [item.description for item in result]
    assert any("landing page" in d.lower() for d in descriptions)
    assert any("analytics" in d.lower() or "dashboard" in d.lower() for d in descriptions)


@pytest.mark.asyncio
async def test_extract_parses_assignees(extractor):
    """Test that assigned_to fields are correctly parsed."""
    mock_resp = _make_mock_response(json.dumps(MOCK_GPT_RESPONSE))
    extractor._client.chat.completions.create = AsyncMock(return_value=mock_resp)

    result = await extractor.extract(SAMPLE_TRANSCRIPT)

    assignees = [item.assigned_to for item in result]
    assert "Bob" in assignees
    assert "Charlie" in assignees
    assert "Alice" in assignees


@pytest.mark.asyncio
async def test_extract_parses_priorities(extractor):
    """Test that priority levels are correctly parsed."""
    mock_resp = _make_mock_response(json.dumps(MOCK_GPT_RESPONSE))
    extractor._client.chat.completions.create = AsyncMock(return_value=mock_resp)

    result = await extractor.extract(SAMPLE_TRANSCRIPT)

    priorities = [item.priority for item in result]
    assert Priority.HIGH in priorities
    assert Priority.MEDIUM in priorities
    assert Priority.LOW in priorities


@pytest.mark.asyncio
async def test_extract_empty_transcript_raises(extractor):
    """Test that an empty transcript raises ActionExtractionError."""
    with pytest.raises(ActionExtractionError, match="empty"):
        await extractor.extract("")


@pytest.mark.asyncio
async def test_extract_whitespace_transcript_raises(extractor):
    """Test that a whitespace-only transcript raises ActionExtractionError."""
    with pytest.raises(ActionExtractionError, match="empty"):
        await extractor.extract("   \n\t  ")


@pytest.mark.asyncio
async def test_extract_invalid_json_raises(extractor):
    """Test that invalid JSON from GPT raises ActionExtractionError."""
    mock_resp = _make_mock_response("Not valid JSON content")
    extractor._client.chat.completions.create = AsyncMock(return_value=mock_resp)

    with pytest.raises(ActionExtractionError, match="invalid JSON"):
        await extractor.extract(SAMPLE_TRANSCRIPT)


@pytest.mark.asyncio
async def test_extract_api_error_raises(extractor):
    """Test that an OpenAI API error is wrapped in ActionExtractionError."""
    extractor._client.chat.completions.create = AsyncMock(
        side_effect=Exception("API connection timeout")
    )

    with pytest.raises(ActionExtractionError, match="GPT API error"):
        await extractor.extract(SAMPLE_TRANSCRIPT)


@pytest.mark.asyncio
async def test_extract_skips_items_without_description(extractor):
    """Test that action items with empty descriptions are filtered out."""
    response_data = {
        "action_items": [
            {"description": "Valid task", "assigned_to": "Bob", "priority": "medium"},
            {"description": "", "assigned_to": "Alice", "priority": "high"},
            {"assigned_to": "Charlie", "priority": "low"},
        ]
    }
    mock_resp = _make_mock_response(json.dumps(response_data))
    extractor._client.chat.completions.create = AsyncMock(return_value=mock_resp)

    result = await extractor.extract(SAMPLE_TRANSCRIPT)

    assert len(result) == 1
    assert result[0].description == "Valid task"


@pytest.mark.asyncio
async def test_extract_unknown_priority_defaults_to_medium(extractor):
    """Test that an unrecognized priority defaults to MEDIUM."""
    response_data = {
        "action_items": [
            {
                "description": "Task with weird priority",
                "assigned_to": "Bob",
                "priority": "super_urgent",
            }
        ]
    }
    mock_resp = _make_mock_response(json.dumps(response_data))
    extractor._client.chat.completions.create = AsyncMock(return_value=mock_resp)

    result = await extractor.extract(SAMPLE_TRANSCRIPT)

    assert len(result) == 1
    assert result[0].priority == Priority.MEDIUM


@pytest.mark.asyncio
async def test_extract_no_action_items_returns_empty(extractor):
    """Test that a response with no action items returns an empty list."""
    response_data = {"action_items": []}
    mock_resp = _make_mock_response(json.dumps(response_data))
    extractor._client.chat.completions.create = AsyncMock(return_value=mock_resp)

    result = await extractor.extract(SAMPLE_TRANSCRIPT)

    assert result == []


@pytest.mark.asyncio
async def test_extract_calls_openai_with_correct_params(extractor):
    """Test that the OpenAI client is called with expected parameters."""
    mock_resp = _make_mock_response(json.dumps(MOCK_GPT_RESPONSE))
    extractor._client.chat.completions.create = AsyncMock(return_value=mock_resp)

    await extractor.extract(SAMPLE_TRANSCRIPT)

    call_kwargs = extractor._client.chat.completions.create.call_args.kwargs
    assert call_kwargs["model"] == "gpt-4"
    assert call_kwargs["temperature"] == 0.2
    assert call_kwargs["response_format"] == {"type": "json_object"}
    assert len(call_kwargs["messages"]) == 2
    assert SAMPLE_TRANSCRIPT in call_kwargs["messages"][1]["content"]
