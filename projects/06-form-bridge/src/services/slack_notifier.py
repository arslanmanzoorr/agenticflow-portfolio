"""Slack notification service for FormBridge.

Sends formatted messages to a Slack channel via incoming webhook
whenever a form submission is processed.
"""

from __future__ import annotations

import logging
from typing import Any

import httpx

from src.config import get_settings
from src.models.webhook import ContactRecord, WebhookPayload

logger = logging.getLogger(__name__)


class SlackNotifier:
    """Sends formatted Slack messages via incoming webhook."""

    def __init__(self) -> None:
        settings = get_settings()
        self._webhook_url = settings.slack_webhook_url
        self._channel = settings.slack_channel
        self._notify_on_error = settings.slack_notify_on_error

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    async def notify_submission(
        self,
        payload: WebhookPayload,
        contact: ContactRecord,
        hubspot_id: str | None = None,
    ) -> bool:
        """Send a Slack notification for a successfully processed submission.

        Parameters
        ----------
        payload:
            The normalised webhook payload.
        contact:
            The mapped contact record.
        hubspot_id:
            HubSpot contact ID if the sync succeeded.

        Returns
        -------
        bool
            ``True`` if the message was sent successfully, ``False`` otherwise.
        """
        if not self._webhook_url:
            logger.debug("Slack webhook URL not configured -- skipping notification")
            return False

        name = f"{contact.first_name or ''} {contact.last_name or ''}".strip() or "Unknown"
        email = contact.email or "N/A"

        blocks = self._build_submission_blocks(
            source=payload.source.value,
            name=name,
            email=email,
            fields_count=len(payload.fields),
            hubspot_id=hubspot_id,
            webhook_id=str(payload.id),
        )

        return await self._send(blocks)

    async def notify_error(self, error_message: str, context: dict[str, Any] | None = None) -> bool:
        """Send a Slack notification for a processing error.

        Parameters
        ----------
        error_message:
            Human-readable description of the error.
        context:
            Optional additional context (source, webhook ID, etc.).

        Returns
        -------
        bool
            ``True`` if the message was sent successfully.
        """
        if not self._webhook_url or not self._notify_on_error:
            return False

        blocks = self._build_error_blocks(error_message, context or {})
        return await self._send(blocks)

    # ------------------------------------------------------------------
    # Block builders
    # ------------------------------------------------------------------

    @staticmethod
    def _build_submission_blocks(
        source: str,
        name: str,
        email: str,
        fields_count: int,
        hubspot_id: str | None,
        webhook_id: str,
    ) -> list[dict[str, Any]]:
        """Build Slack Block Kit blocks for a submission notification."""
        hubspot_status = f"Synced (ID: {hubspot_id})" if hubspot_id else "Skipped"

        return [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "New Form Submission",
                },
            },
            {
                "type": "section",
                "fields": [
                    {"type": "mrkdwn", "text": f"*Source:*\n{source.replace('_', ' ').title()}"},
                    {"type": "mrkdwn", "text": f"*Fields:*\n{fields_count} extracted"},
                ],
            },
            {
                "type": "section",
                "fields": [
                    {"type": "mrkdwn", "text": f"*Name:*\n{name}"},
                    {"type": "mrkdwn", "text": f"*Email:*\n{email}"},
                ],
            },
            {
                "type": "section",
                "fields": [
                    {"type": "mrkdwn", "text": f"*HubSpot:*\n{hubspot_status}"},
                    {"type": "mrkdwn", "text": f"*Webhook ID:*\n`{webhook_id[:8]}...`"},
                ],
            },
            {"type": "divider"},
        ]

    @staticmethod
    def _build_error_blocks(
        error_message: str,
        context: dict[str, Any],
    ) -> list[dict[str, Any]]:
        """Build Slack Block Kit blocks for an error notification."""
        context_lines = "\n".join(f"*{k}:* {v}" for k, v in context.items()) if context else "No additional context"

        return [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "FormBridge Processing Error",
                },
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"```{error_message}```",
                },
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": context_lines,
                },
            },
            {"type": "divider"},
        ]

    # ------------------------------------------------------------------
    # Transport
    # ------------------------------------------------------------------

    async def _send(self, blocks: list[dict[str, Any]]) -> bool:
        """Post a message to the configured Slack webhook."""
        body: dict[str, Any] = {"blocks": blocks}
        if self._channel:
            body["channel"] = self._channel

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.post(self._webhook_url, json=body)

                if resp.status_code == 200:
                    logger.info("Slack notification sent successfully")
                    return True

                logger.error(
                    "Slack webhook returned %s: %s",
                    resp.status_code,
                    resp.text,
                )
                return False

        except httpx.TimeoutException:
            logger.error("Slack webhook request timed out")
            return False
        except Exception as exc:
            logger.error("Slack notification failed: %s", exc)
            return False
