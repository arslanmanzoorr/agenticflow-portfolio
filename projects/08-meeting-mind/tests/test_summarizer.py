"""Tests for the SummarizerService."""

import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.models.meeting import Summary
from src.services.summarizer import SummarizationError, SummarizerService


SAMPLE_TRANSCRIPT = (
    "Alice: Good morning everyone. Let's start with the Q1 results. "
    "Revenue is up 15% compared to last quarter.\n"
    "Bob: That's great news. The marketing campaign really paid off.\n"
    "Alice: Agreed. We need to decide on the budget for Q2. I propose "
    "we increase the marketing budget by 20%.\n"
    "Charlie: I support that. We should also hire two more engineers.\n"
    "Alice: Let's finalize both decisions. Bob, can you draft the budget "
    "proposal by Friday?\n"
    "Bob: Sure, I'll have it ready."
)

MOCK_GPT_RESPONSE = {
    "executive_summary": (
        "The team reviewed Q1 results showing 15% revenue growth. "
        "Key decisions were made to increase the marketing budget by 20% "
        "and hire two additional engineers."
    ),
    "key_decisions": [
        "Increase marketing budget by 20% for Q2",
        "Hire two more engineers",
    ],
    "discussion_topics": [
        "Q1 financial results",
        "Marketing campaign effectiveness",
        "Q2 budget planning",
    ],
    "participants": ["Alice", "Bob", "Charlie"],
    "meeting_date": None,
    "duration_minutes": None,
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
    with patch("src.services.summarizer.get_settings") as mock:
        settings = MagicMock()
        settings.openai_api_key = "sk-test-key"
        settings.openai_model = "gpt-4"
        mock.return_value = settings
        yield settings


@pytest.fixture
def summarizer(mock_settings):
    """Create a SummarizerService with mocked settings."""
    with patch("src.services.summarizer.AsyncOpenAI") as mock_client_cls:
        service = SummarizerService()
        service._client = mock_client_cls.return_value
        yield service


@pytest.mark.asyncio
async def test_summarize_returns_valid_summary(summarizer):
    """Test that summarize() produces a properly structured Summary."""
    mock_resp = _make_mock_response(json.dumps(MOCK_GPT_RESPONSE))
    summarizer._client.chat.completions.create = AsyncMock(return_value=mock_resp)

    result = await summarizer.summarize(SAMPLE_TRANSCRIPT)

    assert isinstance(result, Summary)
    assert "Q1" in result.executive_summary or "revenue" in result.executive_summary.lower()
    assert len(result.key_decisions) == 2
    assert len(result.discussion_topics) == 3
    assert "Alice" in result.participants


@pytest.mark.asyncio
async def test_summarize_key_decisions_extraction(summarizer):
    """Test that key decisions are correctly extracted from the GPT response."""
    mock_resp = _make_mock_response(json.dumps(MOCK_GPT_RESPONSE))
    summarizer._client.chat.completions.create = AsyncMock(return_value=mock_resp)

    result = await summarizer.summarize(SAMPLE_TRANSCRIPT)

    assert any("marketing" in d.lower() for d in result.key_decisions)
    assert any("engineer" in d.lower() for d in result.key_decisions)


@pytest.mark.asyncio
async def test_summarize_empty_transcript_raises(summarizer):
    """Test that an empty transcript raises SummarizationError."""
    with pytest.raises(SummarizationError, match="empty"):
        await summarizer.summarize("")


@pytest.mark.asyncio
async def test_summarize_whitespace_transcript_raises(summarizer):
    """Test that a whitespace-only transcript raises SummarizationError."""
    with pytest.raises(SummarizationError, match="empty"):
        await summarizer.summarize("   \n\t  ")


@pytest.mark.asyncio
async def test_summarize_invalid_json_raises(summarizer):
    """Test that invalid JSON from GPT raises SummarizationError."""
    mock_resp = _make_mock_response("This is not valid JSON at all")
    summarizer._client.chat.completions.create = AsyncMock(return_value=mock_resp)

    with pytest.raises(SummarizationError, match="invalid JSON"):
        await summarizer.summarize(SAMPLE_TRANSCRIPT)


@pytest.mark.asyncio
async def test_summarize_api_error_raises(summarizer):
    """Test that an OpenAI API error is wrapped in SummarizationError."""
    summarizer._client.chat.completions.create = AsyncMock(
        side_effect=Exception("API rate limit exceeded")
    )

    with pytest.raises(SummarizationError, match="GPT API error"):
        await summarizer.summarize(SAMPLE_TRANSCRIPT)


@pytest.mark.asyncio
async def test_summarize_partial_response(summarizer):
    """Test that a partial GPT response still produces a valid Summary."""
    partial = {
        "executive_summary": "Brief meeting about budget.",
        "key_decisions": [],
        "discussion_topics": ["Budget"],
    }
    mock_resp = _make_mock_response(json.dumps(partial))
    summarizer._client.chat.completions.create = AsyncMock(return_value=mock_resp)

    result = await summarizer.summarize(SAMPLE_TRANSCRIPT)

    assert isinstance(result, Summary)
    assert result.executive_summary == "Brief meeting about budget."
    assert result.key_decisions == []
    assert result.participants == []


@pytest.mark.asyncio
async def test_summarize_calls_openai_with_correct_params(summarizer):
    """Test that the OpenAI client is called with expected parameters."""
    mock_resp = _make_mock_response(json.dumps(MOCK_GPT_RESPONSE))
    summarizer._client.chat.completions.create = AsyncMock(return_value=mock_resp)

    await summarizer.summarize(SAMPLE_TRANSCRIPT)

    call_kwargs = summarizer._client.chat.completions.create.call_args.kwargs
    assert call_kwargs["model"] == "gpt-4"
    assert call_kwargs["temperature"] == 0.3
    assert call_kwargs["response_format"] == {"type": "json_object"}
    assert len(call_kwargs["messages"]) == 2
    assert call_kwargs["messages"][0]["role"] == "system"
    assert SAMPLE_TRANSCRIPT in call_kwargs["messages"][1]["content"]
