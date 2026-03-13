"""Webhook router for processing incoming Gmail push notifications."""

import logging
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status

from src.config import Settings, get_settings
from src.models.email import (
    ClassificationResult,
    DraftResponse,
    EmailPayload,
    GmailPushNotification,
)
from src.services.classifier import EmailClassifier
from src.services.gmail_client import GmailClient
from src.services.responder import EmailResponder

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/webhook", tags=["webhook"])


def get_classifier(settings: Settings = Depends(get_settings)) -> EmailClassifier:
    """Dependency injection for email classifier."""
    return EmailClassifier(api_key=settings.openai_api_key)


def get_responder(settings: Settings = Depends(get_settings)) -> EmailResponder:
    """Dependency injection for email responder."""
    return EmailResponder(api_key=settings.openai_api_key)


def get_gmail_client(settings: Settings = Depends(get_settings)) -> GmailClient:
    """Dependency injection for Gmail client."""
    return GmailClient(credentials_path=settings.gmail_credentials_path)


@router.post(
    "/gmail",
    response_model=ClassificationResult,
    status_code=status.HTTP_200_OK,
    summary="Process Gmail push notification",
    description="Receives a Gmail Pub/Sub push notification, fetches the email, "
    "classifies it, and routes to auto-respond or escalate.",
)
async def handle_gmail_webhook(
    notification: GmailPushNotification,
    classifier: EmailClassifier = Depends(get_classifier),
    responder: EmailResponder = Depends(get_responder),
    gmail_client: GmailClient = Depends(get_gmail_client),
) -> ClassificationResult:
    """
    Process an incoming Gmail push notification.

    1. Decode the Pub/Sub message to get the message ID.
    2. Fetch full email content from Gmail API.
    3. Classify the email using OpenAI.
    4. If appropriate, draft and save an auto-response.
    5. If urgent/negative, escalate to human.
    """
    try:
        message_data = notification.message.get("data", "")
        if not message_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Missing message data in push notification",
            )

        email_payload: EmailPayload = await gmail_client.fetch_email(message_data)

        classification: ClassificationResult = await classifier.classify(email_payload)

        if _should_auto_respond(classification):
            draft: DraftResponse = await responder.generate_response(
                email_payload, classification
            )
            await gmail_client.create_draft(
                to=email_payload.sender,
                subject=f"Re: {email_payload.subject}",
                body=draft.body,
            )
            classification.auto_respond = True
            logger.info(
                "Auto-response drafted for message %s", email_payload.message_id
            )

        if _should_escalate(classification):
            classification.escalated = True
            logger.warning(
                "Email %s escalated: category=%s, sentiment=%s",
                email_payload.message_id,
                classification.category,
                classification.sentiment,
            )

        _store_classification(classification)

        return classification

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to process webhook: %s", str(e), exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Webhook processing failed: {str(e)}",
        )


@router.post(
    "/gmail/test",
    response_model=ClassificationResult,
    summary="Test classification with a direct email payload",
    description="Accepts a raw EmailPayload for testing without Gmail integration.",
)
async def test_classification(
    email: EmailPayload,
    classifier: EmailClassifier = Depends(get_classifier),
) -> ClassificationResult:
    """Classify an email directly without going through Gmail."""
    try:
        classification = await classifier.classify(email)
        _store_classification(classification)
        return classification
    except Exception as e:
        logger.error("Test classification failed: %s", str(e), exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Classification failed: {str(e)}",
        )


# In-memory store for recent classifications (production would use a database)
_recent_classifications: list[dict[str, Any]] = []


def _store_classification(result: ClassificationResult) -> None:
    """Store classification result in memory for stats tracking."""
    _recent_classifications.append(result.model_dump())
    # Keep only last 1000 entries in memory
    if len(_recent_classifications) > 1000:
        _recent_classifications.pop(0)


def get_recent_classifications() -> list[dict[str, Any]]:
    """Expose recent classifications for the stats router."""
    return _recent_classifications


def _should_auto_respond(classification: ClassificationResult) -> bool:
    """Determine if an auto-response should be generated."""
    auto_respond_categories = {"billing", "general"}
    return (
        classification.category.value in auto_respond_categories
        and classification.confidence >= 0.8
        and classification.sentiment.value != "negative"
    )


def _should_escalate(classification: ClassificationResult) -> bool:
    """Determine if the email should be escalated to a human."""
    return (
        classification.sentiment.value == "negative"
        or classification.category.value == "technical"
        or classification.confidence < 0.6
    )
