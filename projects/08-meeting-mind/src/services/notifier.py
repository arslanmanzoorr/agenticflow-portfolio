"""Notification service for sharing meeting notes via Slack and email."""

import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Optional

import httpx

from src.config import get_settings
from src.models.meeting import ActionItem, MeetingRecord, Summary

logger = logging.getLogger(__name__)


class NotificationError(Exception):
    """Raised when a notification delivery fails."""


class NotifierService:
    """Posts meeting summaries to Slack and sends email recaps."""

    def __init__(self) -> None:
        self._settings = get_settings()

    # ------------------------------------------------------------------
    # Slack
    # ------------------------------------------------------------------

    async def post_to_slack(
        self,
        meeting: MeetingRecord,
        channel: Optional[str] = None,
    ) -> None:
        """Post a formatted meeting summary to a Slack channel via webhook."""
        webhook_url = self._settings.slack_webhook_url
        if not webhook_url:
            logger.warning("Slack webhook URL is not configured; skipping")
            return

        blocks = self._build_slack_blocks(meeting)
        payload: dict = {"blocks": blocks}
        if channel:
            payload["channel"] = channel

        try:
            async with httpx.AsyncClient(timeout=15) as client:
                resp = await client.post(webhook_url, json=payload)
                resp.raise_for_status()

            logger.info(
                "Meeting notes posted to Slack",
                extra={"meeting_id": meeting.id, "channel": channel},
            )
        except httpx.HTTPError as exc:
            logger.error("Slack notification failed: %s", exc)
            raise NotificationError(f"Slack delivery failed: {exc}") from exc

    @staticmethod
    def _build_slack_blocks(meeting: MeetingRecord) -> list[dict]:
        """Build Slack Block Kit blocks for a meeting summary."""
        blocks: list[dict] = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"Meeting Notes: {meeting.title}",
                },
            },
        ]

        if meeting.summary:
            blocks.append(
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": (
                            f"*Summary*\n{meeting.summary.executive_summary}"
                        ),
                    },
                }
            )

            if meeting.summary.key_decisions:
                decisions = "\n".join(
                    f"- {d}" for d in meeting.summary.key_decisions
                )
                blocks.append(
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": f"*Key Decisions*\n{decisions}",
                        },
                    }
                )

        if meeting.action_items:
            items_text = "\n".join(
                f"- [{item.priority.value.upper()}] {item.description}"
                + (f" (-> {item.assigned_to})" if item.assigned_to else "")
                for item in meeting.action_items
            )
            blocks.append(
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*Action Items*\n{items_text}",
                    },
                }
            )

        return blocks

    # ------------------------------------------------------------------
    # Email
    # ------------------------------------------------------------------

    async def send_email(
        self,
        meeting: MeetingRecord,
        recipients: list[str],
    ) -> None:
        """Send a meeting recap email to the given recipients."""
        settings = self._settings
        if not settings.smtp_host:
            logger.warning("SMTP not configured; skipping email notification")
            return

        subject = f"Meeting Notes: {meeting.title}"
        html_body = self._build_email_html(meeting)

        for recipient in recipients:
            try:
                msg = MIMEMultipart("alternative")
                msg["Subject"] = subject
                msg["From"] = settings.email_from
                msg["To"] = recipient
                msg.attach(MIMEText(html_body, "html"))

                with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as server:
                    server.starttls()
                    if settings.smtp_username:
                        server.login(settings.smtp_username, settings.smtp_password)
                    server.sendmail(settings.email_from, recipient, msg.as_string())

                logger.info(
                    "Email sent",
                    extra={"meeting_id": meeting.id, "recipient": recipient},
                )
            except Exception as exc:
                logger.error(
                    "Failed to send email to %s: %s", recipient, exc
                )
                raise NotificationError(
                    f"Email delivery to {recipient} failed: {exc}"
                ) from exc

    @staticmethod
    def _build_email_html(meeting: MeetingRecord) -> str:
        """Build an HTML email body for the meeting recap."""
        parts: list[str] = [
            "<html><body>",
            f"<h2>{meeting.title}</h2>",
        ]

        if meeting.summary:
            parts.append(f"<h3>Executive Summary</h3><p>{meeting.summary.executive_summary}</p>")

            if meeting.summary.key_decisions:
                parts.append("<h3>Key Decisions</h3><ul>")
                for d in meeting.summary.key_decisions:
                    parts.append(f"<li>{d}</li>")
                parts.append("</ul>")

            if meeting.summary.discussion_topics:
                parts.append("<h3>Discussion Topics</h3><ul>")
                for t in meeting.summary.discussion_topics:
                    parts.append(f"<li>{t}</li>")
                parts.append("</ul>")

        if meeting.action_items:
            parts.append("<h3>Action Items</h3><table border='1' cellpadding='6'>")
            parts.append(
                "<tr><th>Task</th><th>Assigned To</th>"
                "<th>Deadline</th><th>Priority</th></tr>"
            )
            for item in meeting.action_items:
                parts.append(
                    f"<tr><td>{item.description}</td>"
                    f"<td>{item.assigned_to or '-'}</td>"
                    f"<td>{item.deadline or '-'}</td>"
                    f"<td>{item.priority.value}</td></tr>"
                )
            parts.append("</table>")

        parts.append(
            "<hr><p><em>Generated by MeetingMind</em></p></body></html>"
        )
        return "\n".join(parts)
