"""GPT-powered meeting summarization service."""

import json
import logging

from openai import AsyncOpenAI

from src.config import get_settings
from src.models.meeting import Summary

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """\
You are an expert meeting analyst. Given a meeting transcript, produce a
structured JSON summary with the following fields:

{
  "executive_summary": "A concise 2-3 sentence summary of the meeting.",
  "key_decisions": ["List of concrete decisions made during the meeting."],
  "discussion_topics": ["Main topics that were discussed."],
  "participants": ["Names of people who spoke, if identifiable."],
  "meeting_date": "Date of the meeting if mentioned, otherwise null.",
  "duration_minutes": <estimated duration in minutes if determinable, else null>
}

Rules:
- Be concise and factual.
- Only include decisions that were clearly agreed upon.
- Identify participants by name when possible; use role descriptions otherwise.
- Return ONLY valid JSON, no markdown fences.
"""


class SummarizationError(Exception):
    """Raised when summarization fails."""


class SummarizerService:
    """Generates structured meeting summaries using GPT."""

    def __init__(self) -> None:
        settings = get_settings()
        self._client = AsyncOpenAI(api_key=settings.openai_api_key)
        self._model = settings.openai_model

    async def summarize(self, transcript_text: str) -> Summary:
        """Produce a structured summary from a transcript string."""
        if not transcript_text.strip():
            raise SummarizationError("Transcript text is empty")

        logger.info(
            "Generating summary",
            extra={"transcript_length": len(transcript_text)},
        )

        try:
            response = await self._client.chat.completions.create(
                model=self._model,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {
                        "role": "user",
                        "content": (
                            "Please summarize the following meeting transcript:\n\n"
                            f"{transcript_text}"
                        ),
                    },
                ],
                temperature=0.3,
                response_format={"type": "json_object"},
            )

            raw = response.choices[0].message.content or "{}"
            data = json.loads(raw)

            summary = Summary(
                executive_summary=data.get("executive_summary", ""),
                key_decisions=data.get("key_decisions", []),
                discussion_topics=data.get("discussion_topics", []),
                participants=data.get("participants", []),
                meeting_date=data.get("meeting_date"),
                duration_minutes=data.get("duration_minutes"),
            )

            logger.info(
                "Summary generated",
                extra={
                    "decisions": len(summary.key_decisions),
                    "topics": len(summary.discussion_topics),
                },
            )
            return summary

        except json.JSONDecodeError as exc:
            logger.error("Failed to parse GPT response as JSON: %s", exc)
            raise SummarizationError(
                "GPT returned invalid JSON for summary"
            ) from exc
        except Exception as exc:
            logger.error("Summarization failed: %s", exc, exc_info=True)
            raise SummarizationError(f"GPT API error: {exc}") from exc
