"""Email response generation service using OpenAI API."""

import logging

from openai import AsyncOpenAI

from src.models.email import ClassificationResult, DraftResponse, EmailPayload

logger = logging.getLogger(__name__)

RESPONSE_TEMPLATES: dict[str, str] = {
    "billing": (
        "You are a helpful billing support agent. Draft a professional, empathetic "
        "response addressing the customer's billing concern. Include steps they can "
        "take and offer to investigate further if needed."
    ),
    "technical": (
        "You are a technical support specialist. Draft a clear response that "
        "acknowledges the issue, provides initial troubleshooting steps, and "
        "sets expectations for resolution timeline."
    ),
    "sales": (
        "You are a friendly sales representative. Draft a warm response that "
        "addresses the inquiry, highlights relevant product benefits, and "
        "suggests a next step such as a demo or call."
    ),
    "general": (
        "You are a professional customer service representative. Draft a helpful "
        "response that addresses the customer's inquiry clearly and concisely."
    ),
}


class EmailResponder:
    """Generates personalized email responses using OpenAI."""

    def __init__(self, api_key: str, model: str = "gpt-4o-mini") -> None:
        self._client = AsyncOpenAI(api_key=api_key)
        self._model = model

    async def generate_response(
        self, email: EmailPayload, classification: ClassificationResult
    ) -> DraftResponse:
        """
        Generate a personalized response to an email.

        Args:
            email: The original email to respond to.
            classification: The classification result for context.

        Returns:
            DraftResponse containing the generated email response.
        """
        system_prompt = RESPONSE_TEMPLATES.get(
            classification.category.value,
            RESPONSE_TEMPLATES["general"],
        )

        user_prompt = (
            f"Original email:\n"
            f"From: {email.sender}\n"
            f"Subject: {email.subject}\n"
            f"Body: {email.body}\n\n"
            f"Classification: {classification.category.value}\n"
            f"Sentiment: {classification.sentiment.value}\n\n"
            f"Draft a professional response. Do not include subject line, "
            f"just the email body."
        )

        try:
            response = await self._client.chat.completions.create(
                model=self._model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.7,
                max_tokens=512,
            )

            body = response.choices[0].message.content or ""

            return DraftResponse(
                message_id=email.message_id,
                subject=f"Re: {email.subject}",
                body=body.strip(),
                tone="empathetic"
                if classification.sentiment.value == "negative"
                else "professional",
            )

        except Exception as e:
            logger.error("Response generation failed: %s", str(e), exc_info=True)
            raise
