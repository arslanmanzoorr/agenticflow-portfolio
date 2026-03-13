"""Stats router for viewing email classification metrics."""

import logging
from collections import Counter

from fastapi import APIRouter, Query

from src.models.email import EmailStats, RecentClassification
from src.routers.webhook import get_recent_classifications

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/stats", tags=["stats"])


@router.get(
    "",
    response_model=EmailStats,
    summary="Get classification statistics",
    description="Returns aggregated counts of email classifications by category and sentiment.",
)
async def get_stats() -> EmailStats:
    """Return aggregated email classification statistics."""
    classifications = get_recent_classifications()

    if not classifications:
        return EmailStats()

    category_counts = Counter(c["category"] for c in classifications)
    sentiment_counts = Counter(c["sentiment"] for c in classifications)
    auto_responded = sum(1 for c in classifications if c.get("auto_respond", False))
    escalated = sum(1 for c in classifications if c.get("escalated", False))
    avg_confidence = sum(c["confidence"] for c in classifications) / len(
        classifications
    )

    return EmailStats(
        total_processed=len(classifications),
        by_category=dict(category_counts),
        by_sentiment=dict(sentiment_counts),
        auto_responded=auto_responded,
        escalated=escalated,
        avg_confidence=round(avg_confidence, 3),
    )


@router.get(
    "/recent",
    response_model=list[RecentClassification],
    summary="Get recent classifications",
    description="Returns the most recent email classifications.",
)
async def get_recent(
    limit: int = Query(default=20, ge=1, le=100, description="Number of results"),
) -> list[RecentClassification]:
    """Return the most recent classifications."""
    classifications = get_recent_classifications()
    recent = classifications[-limit:]
    recent.reverse()

    return [
        RecentClassification(
            message_id=c["message_id"],
            sender=c.get("sender", "unknown"),
            subject=c.get("subject", ""),
            category=c["category"],
            sentiment=c["sentiment"],
            confidence=c["confidence"],
            classified_at=c["classified_at"],
            auto_respond=c.get("auto_respond", False),
        )
        for c in recent
    ]
