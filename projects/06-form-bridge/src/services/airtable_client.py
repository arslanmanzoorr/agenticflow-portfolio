"""Airtable integration for logging submissions and managing contacts."""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Any

import httpx

from src.config import get_settings
from src.models.webhook import ContactRecord, FormSource, WebhookPayload

logger = logging.getLogger(__name__)

_BASE_URL = "https://api.airtable.com/v0"


class AirtableClient:
    """Async Airtable REST API client."""

    def __init__(self) -> None:
        settings = get_settings()
        self._api_key = settings.airtable_api_key
        self._base_id = settings.airtable_base_id
        self._submissions_table = settings.airtable_submissions_table
        self._contacts_table = settings.airtable_contacts_table
        self._headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _client(self) -> httpx.AsyncClient:
        return httpx.AsyncClient(
            base_url=f"{_BASE_URL}/{self._base_id}",
            headers=self._headers,
            timeout=30.0,
        )

    async def _create_record(self, table: str, fields: dict[str, Any]) -> str | None:
        """Create a record in the given table and return its Airtable ID."""
        async with self._client() as client:
            resp = await client.post(
                f"/{table}",
                json={"fields": fields, "typecast": True},
            )
            if resp.status_code == 200:
                record_id = resp.json().get("id")
                logger.info("Created Airtable record %s in %s", record_id, table)
                return record_id
            logger.error(
                "Airtable create in %s failed: %s %s", table, resp.status_code, resp.text
            )
            return None

    async def _find_record(self, table: str, formula: str) -> dict[str, Any] | None:
        """Find a single record by formula."""
        async with self._client() as client:
            resp = await client.get(
                f"/{table}",
                params={"filterByFormula": formula, "maxRecords": "1"},
            )
            if resp.status_code == 200:
                records = resp.json().get("records", [])
                return records[0] if records else None
            logger.error("Airtable search in %s failed: %s", table, resp.status_code)
            return None

    async def _update_record(self, table: str, record_id: str, fields: dict[str, Any]) -> bool:
        """Update an existing record."""
        async with self._client() as client:
            resp = await client.patch(
                f"/{table}/{record_id}",
                json={"fields": fields, "typecast": True},
            )
            if resp.status_code == 200:
                logger.info("Updated Airtable record %s in %s", record_id, table)
                return True
            logger.error(
                "Airtable update %s/%s failed: %s %s",
                table, record_id, resp.status_code, resp.text,
            )
            return False

    # ------------------------------------------------------------------
    # Submissions
    # ------------------------------------------------------------------

    async def log_submission(self, payload: WebhookPayload, contact: ContactRecord) -> str | None:
        """Log a form submission to the Submissions table."""
        field_summary = {f.key: f.value for f in payload.fields[:20]}

        fields: dict[str, Any] = {
            "Webhook ID": str(payload.id),
            "Source": payload.source.value,
            "Email": contact.email or "",
            "Name": f"{contact.first_name or ''} {contact.last_name or ''}".strip(),
            "Fields": str(field_summary),
            "Received At": payload.received_at.isoformat(),
            "Status": "processed",
        }

        return await self._create_record(self._submissions_table, fields)

    # ------------------------------------------------------------------
    # Contacts
    # ------------------------------------------------------------------

    async def upsert_contact(self, contact: ContactRecord) -> str | None:
        """Create or update a contact in the Contacts table."""
        if not contact.email:
            logger.warning("Cannot upsert Airtable contact without email")
            return None

        formula = f"{{Email}} = '{contact.email}'"
        existing = await self._find_record(self._contacts_table, formula)

        fields: dict[str, Any] = {
            "Email": contact.email,
            "First Name": contact.first_name or "",
            "Last Name": contact.last_name or "",
            "Phone": contact.phone or "",
            "Company": contact.company or "",
            "Source": contact.source.value if contact.source else "custom",
            "Last Updated": datetime.utcnow().isoformat(),
        }

        if existing:
            record_id = existing["id"]
            await self._update_record(self._contacts_table, record_id, fields)
            return record_id

        fields["Created At"] = datetime.utcnow().isoformat()
        return await self._create_record(self._contacts_table, fields)

    # ------------------------------------------------------------------
    # Funnel tracking
    # ------------------------------------------------------------------

    async def update_funnel_stage(
        self, email: str, stage: str, metadata: dict[str, Any] | None = None
    ) -> bool:
        """Update the conversion funnel stage for a contact."""
        formula = f"{{Email}} = '{email}'"
        record = await self._find_record(self._contacts_table, formula)
        if not record:
            logger.warning("Contact %s not found in Airtable for funnel update", email)
            return False

        fields: dict[str, Any] = {
            "Funnel Stage": stage,
            "Last Updated": datetime.utcnow().isoformat(),
        }
        if metadata:
            fields["Funnel Notes"] = str(metadata)

        return await self._update_record(self._contacts_table, record["id"], fields)
