"""Extract structured action items from meeting transcripts using GPT."""

import json
import logging

from openai import AsyncOpenAI

from src.config import get_settings
from src.models.meeting import ActionItem, Priority

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """\
You are an expert at identifying action items from meeting transcripts.
Analyze the transcript and extract every actionable task.

Return a JSON object with a single key "action_items" containing an array.
Each element must have:

{
  "description": "Clear, concise description of what needs to be done.",
  "assigned_to": "Name of the person responsible, or null if unclear.",
  "deadline": "Deadline or timeframe mentioned, or null if not specified.",
  "priority": "low | medium | high | critical"
}

Rules:
- Only include genuine action items, not discussion points.
- Infer priority from urgency cues in the conversation.
- Default to "medium" priority when urgency is unclear.
- Return ONLY valid JSON, no markdown fences.
"""


class ActionExtractionError(Exception):
    """Raised when action item extraction fails."""


class ActionExtractorService:
    """Extracts structured action items from transcripts via GPT."""

    def __init__(self) -> None:
        settings = get_settings()
        self._client = AsyncOpenAI(api_key=settings.openai_api_key)
        self._model = settings.openai_model

    async def extract(self, transcript_text: str) -> list[ActionItem]:
        """Extract action items from a transcript string."""
        if not transcript_text.strip():
            raise ActionExtractionError("Transcript text is empty")

        logger.info(
            "Extracting action items",
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
                            "Extract all action items from this meeting "
                            "transcript:\n\n"
                            f"{transcript_text}"
                        ),
                    },
                ],
                temperature=0.2,
                response_format={"type": "json_object"},
            )

            raw = response.choices[0].message.content or "{}"
            data = json.loads(raw)
            raw_items = data.get("action_items", [])

            items = [
                ActionItem(
                    description=item.get("description", ""),
                    assigned_to=item.get("assigned_to"),
                    deadline=item.get("deadline"),
                    priority=self._parse_priority(item.get("priority", "medium")),
                )
                for item in raw_items
                if item.get("description")
            ]

            logger.info("Extracted %d action items", len(items))
            return items

        except json.JSONDecodeError as exc:
            logger.error("Failed to parse GPT response as JSON: %s", exc)
            raise ActionExtractionError(
                "GPT returned invalid JSON for action items"
            ) from exc
        except Exception as exc:
            logger.error("Action extraction failed: %s", exc, exc_info=True)
            raise ActionExtractionError(f"GPT API error: {exc}") from exc

    @staticmethod
    def _parse_priority(value: str) -> Priority:
        """Safely parse a priority string, defaulting to MEDIUM."""
        try:
            return Priority(value.lower())
        except ValueError:
            return Priority.MEDIUM
