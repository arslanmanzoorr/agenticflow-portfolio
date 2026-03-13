"""Alert service for monitoring review sentiment and sending Slack notifications."""

from __future__ import annotations

import logging
import uuid
from datetime import datetime, timedelta
from typing import Any

import httpx

from api.src.config import Settings, get_settings
from api.src.models.review import (
    AlertItem,
    AlertsResponse,
    Review,
    SentimentResult,
)

logger = logging.getLogger(__name__)


class AlertError(Exception):
    """Raised when an alert operation fails."""


class AlertService:
    """Checks sentiment scores against a threshold and dispatches Slack alerts."""

    def __init__(self, settings: Settings | None = None) -> None:
        self._settings = settings or get_settings()
        self._webhook_url = self._settings.slack_webhook_url
        self._negative_threshold = self._settings.negative_threshold
        self._alert_min_rating = self._settings.alert_min_rating
        # In-memory alert store (swap for a DB / Airtable in production)
        self._alerts: list[AlertItem] = []

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    async def check_alerts(
        self,
        review: Review,
        sentiment: SentimentResult,
    ) -> AlertItem | None:
        """Evaluate a review against alerting rules.

        An alert is created when:
        - The overall sentiment score is below the negative threshold, OR
        - The star rating is at or below the minimum alert rating.

        If an alert is triggered, a Slack notification is dispatched and the
        alert is stored.

        Returns:
            The created ``AlertItem`` if an alert was triggered, else ``None``.
        """
        reasons: list[str] = []

        if sentiment.overall_score <= self._negative_threshold:
            reasons.append(
                f"Sentiment score ({sentiment.overall_score:.2f}) below "
                f"threshold ({self._negative_threshold})"
            )

        if review.rating <= self._alert_min_rating:
            reasons.append(
                f"Rating ({review.rating}) at or below "
                f"alert minimum ({self._alert_min_rating})"
            )

        if not reasons:
            return None

        severity = self._compute_severity(review.rating, sentiment.overall_score)
        alert = AlertItem(
            alert_id=uuid.uuid4().hex[:12],
            review=review,
            sentiment=sentiment,
            reason="; ".join(reasons),
            severity=severity,
        )

        self._alerts.append(alert)
        logger.warning(
            "Alert triggered for review %s: %s (severity=%s)",
            review.review_id,
            alert.reason,
            severity,
        )

        # Best-effort Slack notification
        try:
            await self.send_slack_alert(alert)
        except AlertError:
            logger.warning("Slack alert failed for review %s", review.review_id)

        return alert

    async def send_slack_alert(self, alert: AlertItem) -> None:
        """Send a Slack webhook notification for a negative review alert.

        Args:
            alert: The alert to send.

        Raises:
            AlertError: If the webhook URL is not configured or the request fails.
        """
        if not self._webhook_url:
            raise AlertError("Slack webhook URL not configured")

        review = alert.review
        sentiment = alert.sentiment

        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f":warning: Negative Review Alert ({alert.severity.upper()})",
                },
            },
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*Platform:*\n{review.platform.value}",
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Rating:*\n{'⭐' * int(review.rating)} ({review.rating}/5)",
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Sentiment:*\n{sentiment.label.value} ({sentiment.overall_score:.2f})",
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Business:*\n{review.business_name or 'N/A'}",
                    },
                ],
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": (
                        f"*Review:*\n>{review.text[:500]}"
                        if review.text
                        else "*Review:*\n_No text provided._"
                    ),
                },
            },
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": (
                            f"Reviewer: {review.reviewer_name} | "
                            f"Date: {review.date} | "
                            f"Alert ID: {alert.alert_id}"
                        ),
                    }
                ],
            },
        ]

        payload: dict[str, Any] = {
            "text": f"Negative review alert: {review.rating}/5 on {review.platform.value}",
            "blocks": blocks,
        }

        try:
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.post(self._webhook_url, json=payload)
                response.raise_for_status()
            logger.info("Slack alert sent for review %s", review.review_id)
        except httpx.HTTPError as exc:
            logger.error("Slack webhook failed: %s", exc)
            raise AlertError(f"Slack webhook request failed: {exc}") from exc

    def get_recent_alerts(
        self,
        hours: int = 24,
        severity: str | None = None,
        acknowledged: bool | None = None,
    ) -> AlertsResponse:
        """Return alerts from the last N hours, optionally filtered.

        Args:
            hours: Look-back window in hours (default 24).
            severity: Optional severity filter (low, medium, high, critical).
            acknowledged: Optional filter on acknowledged state.

        Returns:
            An ``AlertsResponse`` with matching alerts.
        """
        cutoff = datetime.utcnow() - timedelta(hours=hours)

        filtered: list[AlertItem] = []
        for alert in self._alerts:
            alert_time = datetime.fromisoformat(alert.created_at)
            if alert_time < cutoff:
                continue
            if severity and alert.severity != severity:
                continue
            if acknowledged is not None and alert.acknowledged != acknowledged:
                continue
            filtered.append(alert)

        unack = sum(1 for a in filtered if not a.acknowledged)

        return AlertsResponse(
            alerts=filtered,
            total_count=len(filtered),
            unacknowledged_count=unack,
        )

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _compute_severity(rating: float, score: float) -> str:
        """Derive alert severity from rating and sentiment score."""
        if rating <= 1 and score <= -0.7:
            return "critical"
        if rating <= 2 or score <= -0.5:
            return "high"
        if score <= -0.3:
            return "medium"
        return "low"
