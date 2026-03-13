"""Airtable CRUD client for ContentEngine records.

Wraps *pyairtable* to persist generated content and editorial calendar entries
in Airtable.  All public methods are async-safe by delegating blocking I/O to
a thread-pool executor.
"""

from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timedelta
from functools import partial
from typing import Any, Optional

from pyairtable import Api

from ..config import Settings, get_settings
from ..models.content import (
    ContentRecord,
    ContentStatus,
    Platform,
    Tone,
)

logger = logging.getLogger(__name__)


class AirtableClient:
    """Async-friendly Airtable client for content records."""

    def __init__(self, settings: Optional[Settings] = None) -> None:
        self._settings = settings or get_settings()
        self._api = Api(self._settings.airtable_api_key)
        self._content_table = self._api.table(
            self._settings.airtable_base_id,
            self._settings.airtable_content_table,
        )
        self._calendar_table = self._api.table(
            self._settings.airtable_base_id,
            self._settings.airtable_calendar_table,
        )

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    async def _run_sync(func: Any, *args: Any, **kwargs: Any) -> Any:
        """Run a synchronous function in the default executor."""
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, partial(func, *args, **kwargs))

    @staticmethod
    def _record_to_fields(record: ContentRecord) -> dict[str, Any]:
        """Convert a ``ContentRecord`` to an Airtable-compatible field dict."""
        return {
            "ContentID": record.id,
            "Topic": record.topic,
            "Platform": record.platform.value,
            "Tone": record.tone.value,
            "Content": record.content,
            "Hashtags": ", ".join(record.hashtags),
            "ImagePrompt": record.image_prompt or "",
            "CharacterCount": record.character_count,
            "Status": record.status.value,
            "PublishAt": record.publish_at.isoformat() if record.publish_at else "",
            "PublishedAt": record.published_at.isoformat() if record.published_at else "",
            "CreatedAt": record.created_at.isoformat(),
            "UpdatedAt": record.updated_at.isoformat(),
        }

    @staticmethod
    def _fields_to_record(airtable_id: str, fields: dict[str, Any]) -> ContentRecord:
        """Convert Airtable fields back into a ``ContentRecord``."""
        hashtags_raw: str = fields.get("Hashtags", "")
        hashtags = [h.strip() for h in hashtags_raw.split(",") if h.strip()] if hashtags_raw else []

        def _parse_dt(value: str | None) -> Optional[datetime]:
            if not value:
                return None
            try:
                return datetime.fromisoformat(value)
            except (ValueError, TypeError):
                return None

        return ContentRecord(
            id=fields.get("ContentID", ""),
            topic=fields.get("Topic", ""),
            platform=Platform(fields.get("Platform", "linkedin")),
            tone=Tone(fields.get("Tone", "professional")),
            content=fields.get("Content", ""),
            hashtags=hashtags,
            image_prompt=fields.get("ImagePrompt") or None,
            character_count=int(fields.get("CharacterCount", 0)),
            status=ContentStatus(fields.get("Status", "draft")),
            publish_at=_parse_dt(fields.get("PublishAt")),
            published_at=_parse_dt(fields.get("PublishedAt")),
            created_at=_parse_dt(fields.get("CreatedAt")) or datetime.utcnow(),
            updated_at=_parse_dt(fields.get("UpdatedAt")) or datetime.utcnow(),
            airtable_record_id=airtable_id,
        )

    # ------------------------------------------------------------------
    # CRUD: Generated Content table
    # ------------------------------------------------------------------

    async def create_content(self, record: ContentRecord) -> ContentRecord:
        """Insert a new content record into Airtable.

        Returns:
            The record updated with the Airtable record ID.
        """
        fields = self._record_to_fields(record)
        logger.info("Creating Airtable record for content_id=%s", record.id)
        result = await self._run_sync(self._content_table.create, fields)
        record.airtable_record_id = result["id"]
        return record

    async def get_content(self, content_id: str) -> Optional[ContentRecord]:
        """Retrieve a content record by its application-level ID.

        Returns:
            The matching ``ContentRecord`` or ``None`` if not found.
        """
        formula = f"{{ContentID}} = '{content_id}'"
        records = await self._run_sync(self._content_table.all, formula=formula)
        if not records:
            return None
        rec = records[0]
        return self._fields_to_record(rec["id"], rec["fields"])

    async def update_content(
        self,
        airtable_record_id: str,
        updates: dict[str, Any],
    ) -> dict[str, Any]:
        """Partially update a content record in Airtable.

        Args:
            airtable_record_id: The Airtable record ``id`` (not ContentID).
            updates: Dict of field names to new values.

        Returns:
            The raw Airtable API response.
        """
        logger.info("Updating Airtable record %s", airtable_record_id)
        return await self._run_sync(self._content_table.update, airtable_record_id, updates)

    async def delete_content(self, airtable_record_id: str) -> dict[str, Any]:
        """Delete a content record by its Airtable record ID."""
        logger.info("Deleting Airtable record %s", airtable_record_id)
        return await self._run_sync(self._content_table.delete, airtable_record_id)

    async def list_content(
        self,
        *,
        status: Optional[ContentStatus] = None,
        platform: Optional[Platform] = None,
        limit: int = 100,
    ) -> list[ContentRecord]:
        """List content records with optional filters.

        Args:
            status: Filter by content status.
            platform: Filter by platform.
            limit: Maximum number of records to return.

        Returns:
            A list of ``ContentRecord`` instances.
        """
        formula_parts: list[str] = []
        if status:
            formula_parts.append(f"{{Status}} = '{status.value}'")
        if platform:
            formula_parts.append(f"{{Platform}} = '{platform.value}'")

        formula = (
            f"AND({', '.join(formula_parts)})" if len(formula_parts) > 1
            else formula_parts[0] if formula_parts
            else None
        )

        kwargs: dict[str, Any] = {"max_records": limit}
        if formula:
            kwargs["formula"] = formula

        raw_records = await self._run_sync(self._content_table.all, **kwargs)
        return [self._fields_to_record(r["id"], r["fields"]) for r in raw_records]

    # ------------------------------------------------------------------
    # CRUD: Content Calendar table
    # ------------------------------------------------------------------

    async def get_calendar_topics(self, days_ahead: int = 7) -> list[dict[str, Any]]:
        """Fetch upcoming topics from the Content Calendar table.

        Args:
            days_ahead: How many days into the future to look.

        Returns:
            A list of dicts with keys ``topic``, ``platform``, ``tone``, and
            ``scheduled_date``.
        """
        today = datetime.utcnow().date().isoformat()
        future = (datetime.utcnow() + timedelta(days=days_ahead)).date().isoformat()
        formula = f"AND({{ScheduledDate}} >= '{today}', {{ScheduledDate}} <= '{future}')"

        records = await self._run_sync(self._calendar_table.all, formula=formula)

        topics: list[dict[str, Any]] = []
        for rec in records:
            fields = rec["fields"]
            topics.append(
                {
                    "topic": fields.get("Topic", ""),
                    "platform": fields.get("Platform", "linkedin"),
                    "tone": fields.get("Tone", "professional"),
                    "scheduled_date": fields.get("ScheduledDate", ""),
                    "keywords": [
                        k.strip()
                        for k in fields.get("Keywords", "").split(",")
                        if k.strip()
                    ],
                }
            )
        return topics

    # ------------------------------------------------------------------
    # Analytics helpers
    # ------------------------------------------------------------------

    async def get_analytics(self) -> dict[str, Any]:
        """Compute basic content analytics from Airtable records.

        Returns:
            A dict suitable for constructing an ``AnalyticsResponse``.
        """
        all_records = await self._run_sync(self._content_table.all)

        total = len(all_records)
        by_status: dict[str, int] = {}
        by_platform: dict[str, dict[str, Any]] = {}
        today_count = 0
        week_count = 0
        now = datetime.utcnow()
        week_ago = now - timedelta(days=7)

        for rec in all_records:
            fields = rec["fields"]
            status_val = fields.get("Status", "draft")
            platform_val = fields.get("Platform", "linkedin")
            char_count = int(fields.get("CharacterCount", 0))

            # By status
            by_status[status_val] = by_status.get(status_val, 0) + 1

            # By platform
            if platform_val not in by_platform:
                by_platform[platform_val] = {
                    "total_posts": 0,
                    "published": 0,
                    "scheduled": 0,
                    "drafts": 0,
                    "total_chars": 0,
                }
            entry = by_platform[platform_val]
            entry["total_posts"] += 1
            entry["total_chars"] += char_count
            if status_val == "published":
                entry["published"] += 1
            elif status_val == "scheduled":
                entry["scheduled"] += 1
            elif status_val == "draft":
                entry["drafts"] += 1

            # Time-based counts
            created_str = fields.get("CreatedAt", "")
            if created_str:
                try:
                    created_dt = datetime.fromisoformat(created_str)
                    if created_dt.date() == now.date():
                        today_count += 1
                    if created_dt >= week_ago:
                        week_count += 1
                except (ValueError, TypeError):
                    pass

        platform_analytics = []
        for plat, data in by_platform.items():
            avg_chars = data["total_chars"] / data["total_posts"] if data["total_posts"] else 0
            platform_analytics.append(
                {
                    "platform": plat,
                    "total_posts": data["total_posts"],
                    "published": data["published"],
                    "scheduled": data["scheduled"],
                    "drafts": data["drafts"],
                    "avg_character_count": round(avg_chars, 1),
                }
            )

        return {
            "total_content": total,
            "by_platform": platform_analytics,
            "by_status": by_status,
            "generated_today": today_count,
            "generated_this_week": week_count,
        }
