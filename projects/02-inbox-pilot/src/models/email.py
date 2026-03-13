"""Pydantic models for email classification and processing."""

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class EmailCategory(str, Enum):
    """Supported email classification categories."""

    BILLING = "billing"
    TECHNICAL = "technical"
    SALES = "sales"
    SPAM = "spam"
    GENERAL = "general"


class Sentiment(str, Enum):
    """Email sentiment classification."""

    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"


class EmailPayload(BaseModel):
    """Incoming email data from Gmail webhook."""

    message_id: str = Field(..., description="Unique Gmail message ID")
    sender: str = Field(..., description="Sender email address")
    subject: str = Field(..., description="Email subject line")
    body: str = Field(..., description="Email body text")
    received_at: datetime = Field(
        default_factory=datetime.utcnow, description="Timestamp when email was received"
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "message_id": "msg_abc123",
                    "sender": "customer@example.com",
                    "subject": "Billing issue with my account",
                    "body": "I was charged twice for my subscription last month.",
                }
            ]
        }
    }


class ClassificationResult(BaseModel):
    """Result of email classification by AI."""

    message_id: str = Field(..., description="Reference to original email")
    category: EmailCategory = Field(..., description="Classified category")
    sentiment: Sentiment = Field(..., description="Detected sentiment")
    confidence: float = Field(
        ..., ge=0.0, le=1.0, description="Classification confidence score"
    )
    summary: str = Field(..., description="Brief summary of the email")
    auto_respond: bool = Field(
        default=False, description="Whether an auto-response was triggered"
    )
    escalated: bool = Field(
        default=False, description="Whether the email was escalated"
    )
    classified_at: datetime = Field(default_factory=datetime.utcnow)


class DraftResponse(BaseModel):
    """AI-generated draft response for an email."""

    message_id: str = Field(..., description="Reference to original email")
    subject: str = Field(..., description="Response subject line")
    body: str = Field(..., description="Generated response body")
    tone: str = Field(default="professional", description="Response tone")


class EmailStats(BaseModel):
    """Aggregated email classification statistics."""

    total_processed: int = Field(default=0, description="Total emails processed")
    by_category: dict[str, int] = Field(
        default_factory=dict, description="Count per category"
    )
    by_sentiment: dict[str, int] = Field(
        default_factory=dict, description="Count per sentiment"
    )
    auto_responded: int = Field(default=0, description="Emails auto-responded to")
    escalated: int = Field(default=0, description="Emails escalated")
    avg_confidence: float = Field(
        default=0.0, description="Average classification confidence"
    )


class RecentClassification(BaseModel):
    """A recent classification entry for display."""

    message_id: str
    sender: str
    subject: str
    category: EmailCategory
    sentiment: Sentiment
    confidence: float
    classified_at: datetime
    auto_respond: bool = False


class GmailPushNotification(BaseModel):
    """Gmail Pub/Sub push notification payload."""

    message: dict = Field(..., description="Pub/Sub message wrapper")
    subscription: Optional[str] = Field(
        default=None, description="Subscription identifier"
    )
