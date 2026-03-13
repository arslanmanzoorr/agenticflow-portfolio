"""Gmail API client for reading emails and managing drafts."""

import base64
import logging
from email.mime.text import MIMEText
from typing import Any, Optional

from src.models.email import EmailPayload

logger = logging.getLogger(__name__)


class GmailClient:
    """Wrapper for Gmail API operations."""

    def __init__(self, credentials_path: str) -> None:
        self._credentials_path = credentials_path
        self._service: Optional[Any] = None

    def _get_service(self) -> Any:
        """
        Build and return an authenticated Gmail API service.

        Uses OAuth2 credentials from the configured file path.
        """
        if self._service is not None:
            return self._service

        try:
            from google.oauth2.credentials import Credentials
            from googleapiclient.discovery import build

            creds = Credentials.from_authorized_user_file(
                self._credentials_path,
                scopes=["https://www.googleapis.com/auth/gmail.modify"],
            )
            self._service = build("gmail", "v1", credentials=creds)
            return self._service

        except FileNotFoundError:
            logger.error(
                "Gmail credentials not found at %s", self._credentials_path
            )
            raise
        except Exception as e:
            logger.error("Failed to build Gmail service: %s", str(e))
            raise

    async def fetch_email(self, encoded_data: str) -> EmailPayload:
        """
        Fetch email content from Gmail using a Pub/Sub notification.

        Args:
            encoded_data: Base64-encoded Pub/Sub message data containing
                         the email history ID.

        Returns:
            EmailPayload with the full email content.
        """
        try:
            decoded = base64.urlsafe_b64decode(encoded_data).decode("utf-8")
            import json

            notification_data = json.loads(decoded)
            history_id = notification_data.get("historyId")

            service = self._get_service()

            history = (
                service.users()
                .history()
                .list(userId="me", startHistoryId=history_id, historyTypes=["messageAdded"])
                .execute()
            )

            messages = []
            for record in history.get("history", []):
                for msg in record.get("messagesAdded", []):
                    messages.append(msg["message"]["id"])

            if not messages:
                raise ValueError("No new messages found in history")

            message_id = messages[0]
            msg = (
                service.users()
                .messages()
                .get(userId="me", id=message_id, format="full")
                .execute()
            )

            headers = {
                h["name"].lower(): h["value"]
                for h in msg.get("payload", {}).get("headers", [])
            }

            body = self._extract_body(msg.get("payload", {}))

            return EmailPayload(
                message_id=message_id,
                sender=headers.get("from", "unknown@unknown.com"),
                subject=headers.get("subject", "(No Subject)"),
                body=body,
            )

        except Exception as e:
            logger.error("Failed to fetch email: %s", str(e), exc_info=True)
            raise

    async def create_draft(self, to: str, subject: str, body: str) -> str:
        """
        Create a draft email in Gmail.

        Args:
            to: Recipient email address.
            subject: Email subject line.
            body: Email body text.

        Returns:
            The draft ID.
        """
        try:
            service = self._get_service()

            message = MIMEText(body)
            message["to"] = to
            message["subject"] = subject

            raw = base64.urlsafe_b64encode(message.as_bytes()).decode("utf-8")

            draft = (
                service.users()
                .drafts()
                .create(userId="me", body={"message": {"raw": raw}})
                .execute()
            )

            draft_id = draft["id"]
            logger.info("Created draft %s for %s", draft_id, to)
            return draft_id

        except Exception as e:
            logger.error("Failed to create draft: %s", str(e), exc_info=True)
            raise

    @staticmethod
    def _extract_body(payload: dict[str, Any]) -> str:
        """Extract plain text body from Gmail message payload."""
        if payload.get("mimeType") == "text/plain":
            data = payload.get("body", {}).get("data", "")
            return base64.urlsafe_b64decode(data).decode("utf-8")

        for part in payload.get("parts", []):
            if part.get("mimeType") == "text/plain":
                data = part.get("body", {}).get("data", "")
                return base64.urlsafe_b64decode(data).decode("utf-8")

        return ""
