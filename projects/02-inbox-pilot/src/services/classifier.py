"""Email classification service using OpenAI API."""

import json
import logging
from typing import Any

from openai import AsyncOpenAI

from src.models.email import (
    ClassificationResult,
    EmailCategory,
    EmailPayload,
    Sentiment,
)

logger = logging.getLogger(__name__)

CLASSIFICATION_PROMPT = """You are an email classification assistant. Analyze the following email and return a JSON object with these fields:

- category: one of "billing", "technical", "sales", "spam", "general"
- sentiment: one of "positive", "neutral", "negative"
- confidence: a float between 0.0 and 1.0 indicating your confidence
- summary: a brief one-sentence summary of the email

Email:
From: {sender}
Subject: {subject}
Body: {body}

Return ONLY valid JSON, no other text."""


class EmailClassifier:
    """Classifies emails using OpenAI's GPT models."""

    def __init__(self, api_key: str, model: str = "gpt-4o-mini") -> None:
        self._client = AsyncOpenAI(api_key=api_key)
        self._model = model

    async def classify(self, email: EmailPayload) -> ClassificationResult:
        """
        Classify an email into a category and sentiment.

        Args:
            email: The email payload to classify.

        Returns:
            ClassificationResult with category, sentiment, confidence, and summary.

        Raises:
            ValueError: If the AI response cannot be parsed.
        """
        prompt = CLASSIFICATION_PROMPT.format(
            sender=email.sender,
            subject=email.subject,
            body=email.body[:2000],  # Truncate to avoid token limits
        )

        try:
            response = await self._client.chat.completions.create(
                model=self._model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a precise email classifier. Always respond with valid JSON.",
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.1,
                max_tokens=256,
                response_format={"type": "json_object"},
            )

            raw_content = response.choices[0].message.content
            if not raw_content:
                raise ValueError("Empty response from OpenAI")

            parsed: dict[str, Any] = json.loads(raw_content)

            return ClassificationResult(
                message_id=email.message_id,
                category=EmailCategory(parsed["category"]),
                sentiment=Sentiment(parsed["sentiment"]),
                confidence=float(parsed["confidence"]),
                summary=parsed["summary"],
            )

        except json.JSONDecodeError as e:
            logger.error("Failed to parse classification response: %s", str(e))
            raise ValueError(f"Invalid JSON from classifier: {str(e)}")
        except KeyError as e:
            logger.error("Missing field in classification response: %s", str(e))
            raise ValueError(f"Missing field in classification: {str(e)}")
        except Exception as e:
            logger.error("Classification failed: %s", str(e), exc_info=True)
            raise
