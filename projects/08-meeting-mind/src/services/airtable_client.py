"""Airtable client for persisting meetings, summaries, and action items."""

import logging
from typing import Any, Optional

from pyairtable import Api

from src.config import get_settings
from src.models.meeting import ActionItem, MeetingRecord, Summary, Transcript

logger = logging.getLogger(__name__)


class AirtableError(Exception):
    """Raised when an Airtable operation fails."""


class AirtableClient:
    """Stores and retrieves meeting data from Airtable."""

    def __init__(self) -> None:
        settings = get_settings()
        self._api = Api(settings.airtable_api_key)
        self._base_id = settings.airtable_base_id
        self._meetings_table = settings.airtable_meetings_table
        self._actions_table = settings.airtable_actions_table

    @property
    def _meetings(self):
        return self._api.table(self._base_id, self._meetings_table)

    @property
    def _actions(self):
        return self._api.table(self._base_id, self._actions_table)

    async def save_meeting(self, meeting: MeetingRecord) -> str:
        """Persist a meeting record to Airtable and return the Airtable ID."""
        try:
            fields: dict[str, Any] = {
                "MeetingID": meeting.id,
                "Title": meeting.title,
                "Status": meeting.status,
                "CreatedAt": meeting.created_at.isoformat(),
            }

            if meeting.audio_filename:
                fields["AudioFile"] = meeting.audio_filename

            if meeting.transcript:
                fields["TranscriptText"] = meeting.transcript.full_text[:100_000]
                fields["Language"] = meeting.transcript.language
                fields["DurationSeconds"] = meeting.transcript.duration_seconds

            if meeting.summary:
                fields["ExecutiveSummary"] = meeting.summary.executive_summary
                fields["KeyDecisions"] = "\n".join(meeting.summary.key_decisions)
                fields["DiscussionTopics"] = "\n".join(
                    meeting.summary.discussion_topics
                )
                fields["Participants"] = ", ".join(meeting.summary.participants)

            record = self._meetings.create(fields)
            airtable_id = record["id"]
            logger.info(
                "Meeting saved to Airtable",
                extra={"meeting_id": meeting.id, "airtable_id": airtable_id},
            )
            return airtable_id

        except Exception as exc:
            logger.error("Failed to save meeting to Airtable: %s", exc)
            raise AirtableError(f"Airtable save failed: {exc}") from exc

    async def save_action_items(
        self, meeting_id: str, items: list[ActionItem]
    ) -> list[str]:
        """Persist action items linked to a meeting. Returns Airtable IDs."""
        created_ids: list[str] = []
        for item in items:
            try:
                fields: dict[str, Any] = {
                    "MeetingID": meeting_id,
                    "Description": item.description,
                    "Priority": item.priority.value,
                }
                if item.assigned_to:
                    fields["AssignedTo"] = item.assigned_to
                if item.deadline:
                    fields["Deadline"] = item.deadline

                record = self._actions.create(fields)
                created_ids.append(record["id"])
            except Exception as exc:
                logger.error(
                    "Failed to save action item to Airtable: %s", exc
                )

        logger.info(
            "Saved %d/%d action items to Airtable",
            len(created_ids),
            len(items),
        )
        return created_ids

    async def get_meeting(self, meeting_id: str) -> Optional[dict[str, Any]]:
        """Retrieve a meeting record by its MeetingID field."""
        try:
            records = self._meetings.all(formula=f"{{MeetingID}}='{meeting_id}'")
            if not records:
                return None
            return records[0]["fields"]
        except Exception as exc:
            logger.error("Failed to fetch meeting from Airtable: %s", exc)
            raise AirtableError(f"Airtable fetch failed: {exc}") from exc

    async def list_meetings(
        self, max_records: int = 50
    ) -> list[dict[str, Any]]:
        """List recent meetings from Airtable."""
        try:
            records = self._meetings.all(
                max_records=max_records,
                sort=["-CreatedAt"],
            )
            return [r["fields"] for r in records]
        except Exception as exc:
            logger.error("Failed to list meetings from Airtable: %s", exc)
            raise AirtableError(f"Airtable list failed: {exc}") from exc

    async def get_action_items(
        self, meeting_id: str
    ) -> list[dict[str, Any]]:
        """Retrieve action items for a given meeting."""
        try:
            records = self._actions.all(
                formula=f"{{MeetingID}}='{meeting_id}'"
            )
            return [r["fields"] for r in records]
        except Exception as exc:
            logger.error(
                "Failed to fetch action items from Airtable: %s", exc
            )
            raise AirtableError(
                f"Airtable action items fetch failed: {exc}"
            ) from exc
