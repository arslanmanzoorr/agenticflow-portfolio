"""HubSpot CRM integration using the v3 API.

Provides async wrappers for creating/updating contacts, creating deals,
and adding engagement notes.
"""

from __future__ import annotations

import logging
from typing import Any

import httpx

from src.config import get_settings
from src.models.webhook import ContactRecord

logger = logging.getLogger(__name__)

_BASE_URL = "https://api.hubapi.com"


class HubSpotClient:
    """Async HubSpot API v3 client."""

    def __init__(self) -> None:
        settings = get_settings()
        self._api_key = settings.hubspot_api_key
        self._headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _client(self) -> httpx.AsyncClient:
        return httpx.AsyncClient(
            base_url=_BASE_URL,
            headers=self._headers,
            timeout=30.0,
        )

    # ------------------------------------------------------------------
    # Contacts
    # ------------------------------------------------------------------

    async def search_contact_by_email(self, email: str) -> dict[str, Any] | None:
        """Search for an existing contact by email address."""
        body = {
            "filterGroups": [
                {
                    "filters": [
                        {"propertyName": "email", "operator": "EQ", "value": email}
                    ]
                }
            ],
            "properties": ["email", "firstname", "lastname", "phone", "company"],
        }
        async with self._client() as client:
            resp = await client.post("/crm/v3/objects/contacts/search", json=body)
            if resp.status_code != 200:
                logger.error("HubSpot search failed: %s %s", resp.status_code, resp.text)
                return None
            results = resp.json().get("results", [])
            return results[0] if results else None

    async def create_contact(self, contact: ContactRecord) -> str | None:
        """Create a new contact and return the HubSpot contact ID."""
        properties: dict[str, Any] = {}
        if contact.email:
            properties["email"] = contact.email
        if contact.first_name:
            properties["firstname"] = contact.first_name
        if contact.last_name:
            properties["lastname"] = contact.last_name
        if contact.phone:
            properties["phone"] = contact.phone
        if contact.company:
            properties["company"] = contact.company

        # Add any custom fields that have a hubspot_ prefix
        for key, value in contact.custom_fields.items():
            if key.startswith("hubspot_"):
                properties[key.removeprefix("hubspot_")] = value

        async with self._client() as client:
            resp = await client.post(
                "/crm/v3/objects/contacts",
                json={"properties": properties},
            )
            if resp.status_code == 201:
                contact_id = resp.json().get("id")
                logger.info("Created HubSpot contact %s for %s", contact_id, contact.email)
                return contact_id

            logger.error("HubSpot create contact failed: %s %s", resp.status_code, resp.text)
            return None

    async def update_contact(self, hubspot_id: str, contact: ContactRecord) -> bool:
        """Update an existing HubSpot contact."""
        properties: dict[str, Any] = {}
        if contact.first_name:
            properties["firstname"] = contact.first_name
        if contact.last_name:
            properties["lastname"] = contact.last_name
        if contact.phone:
            properties["phone"] = contact.phone
        if contact.company:
            properties["company"] = contact.company

        for key, value in contact.custom_fields.items():
            if key.startswith("hubspot_"):
                properties[key.removeprefix("hubspot_")] = value

        if not properties:
            return True

        async with self._client() as client:
            resp = await client.patch(
                f"/crm/v3/objects/contacts/{hubspot_id}",
                json={"properties": properties},
            )
            if resp.status_code == 200:
                logger.info("Updated HubSpot contact %s", hubspot_id)
                return True
            logger.error("HubSpot update failed: %s %s", resp.status_code, resp.text)
            return False

    async def upsert_contact(self, contact: ContactRecord) -> str | None:
        """Create or update a contact. Returns the HubSpot ID."""
        if not contact.email:
            logger.warning("Cannot upsert contact without email")
            return None

        existing = await self.search_contact_by_email(contact.email)
        if existing:
            hubspot_id = existing["id"]
            await self.update_contact(hubspot_id, contact)
            return hubspot_id

        return await self.create_contact(contact)

    # ------------------------------------------------------------------
    # Deals
    # ------------------------------------------------------------------

    async def create_deal(
        self,
        name: str,
        pipeline: str = "default",
        stage: str = "appointmentscheduled",
        amount: float | None = None,
        contact_id: str | None = None,
    ) -> str | None:
        """Create a deal and optionally associate it with a contact."""
        properties: dict[str, Any] = {
            "dealname": name,
            "pipeline": pipeline,
            "dealstage": stage,
        }
        if amount is not None:
            properties["amount"] = str(amount)

        body: dict[str, Any] = {"properties": properties}

        if contact_id:
            body["associations"] = [
                {
                    "to": {"id": contact_id},
                    "types": [
                        {
                            "associationCategory": "HUBSPOT_DEFINED",
                            "associationTypeId": 3,  # deal -> contact
                        }
                    ],
                }
            ]

        async with self._client() as client:
            resp = await client.post("/crm/v3/objects/deals", json=body)
            if resp.status_code == 201:
                deal_id = resp.json().get("id")
                logger.info("Created HubSpot deal %s", deal_id)
                return deal_id
            logger.error("HubSpot create deal failed: %s %s", resp.status_code, resp.text)
            return None

    # ------------------------------------------------------------------
    # Notes / Engagements
    # ------------------------------------------------------------------

    async def add_note(self, contact_id: str, body: str) -> str | None:
        """Add a note engagement associated with a contact."""
        payload: dict[str, Any] = {
            "properties": {"hs_note_body": body, "hs_timestamp": ""},
            "associations": [
                {
                    "to": {"id": contact_id},
                    "types": [
                        {
                            "associationCategory": "HUBSPOT_DEFINED",
                            "associationTypeId": 202,  # note -> contact
                        }
                    ],
                }
            ],
        }

        async with self._client() as client:
            resp = await client.post("/crm/v3/objects/notes", json=payload)
            if resp.status_code == 201:
                note_id = resp.json().get("id")
                logger.info("Added note %s to contact %s", note_id, contact_id)
                return note_id
            logger.error("HubSpot add note failed: %s %s", resp.status_code, resp.text)
            return None
