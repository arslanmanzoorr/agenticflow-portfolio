"""Core domain models for webhook processing."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, EmailStr


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class FormSource(str, Enum):
    """Supported form providers."""

    TYPEFORM = "typeform"
    JOTFORM = "jotform"
    GOOGLE_FORMS = "google_forms"
    GRAVITY_FORMS = "gravity_forms"
    CUSTOM = "custom"


class ProcessingStatus(str, Enum):
    """Webhook processing status."""

    RECEIVED = "received"
    PARSED = "parsed"
    MAPPED = "mapped"
    VALIDATED = "validated"
    SYNCED = "synced"
    FAILED = "failed"


class TransformationType(str, Enum):
    """Available field transformations."""

    CAPITALIZE = "capitalize"
    LOWERCASE = "lowercase"
    UPPERCASE = "uppercase"
    FORMAT_PHONE = "format_phone"
    PARSE_DATE = "parse_date"
    STRIP = "strip"
    TITLE_CASE = "title_case"
    NONE = "none"


# ---------------------------------------------------------------------------
# Form data models
# ---------------------------------------------------------------------------

class FormField(BaseModel):
    """A single normalised form field."""

    key: str = Field(..., description="Normalised field key, e.g. 'email'")
    label: str = Field(default="", description="Human-readable label from the form")
    value: Any = Field(default=None, description="Submitted value")
    field_type: str = Field(default="text", description="text, email, phone, date, select, …")


class WebhookPayload(BaseModel):
    """Normalised representation of an incoming webhook submission."""

    id: UUID = Field(default_factory=uuid4)
    source: FormSource
    raw_payload: dict[str, Any] = Field(default_factory=dict)
    fields: list[FormField] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
    received_at: datetime = Field(default_factory=datetime.utcnow)


# ---------------------------------------------------------------------------
# Mapping configuration
# ---------------------------------------------------------------------------

class FieldMapping(BaseModel):
    """Maps a source form field to a CRM destination field."""

    id: UUID = Field(default_factory=uuid4)
    name: str = Field(..., description="Friendly mapping name")
    source: FormSource
    source_field: str = Field(..., description="Key in normalised payload")
    destination_field: str = Field(..., description="CRM field name, e.g. 'hubspot.email'")
    transformation: TransformationType = TransformationType.NONE
    required: bool = False
    default_value: Any = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


# ---------------------------------------------------------------------------
# Processing log
# ---------------------------------------------------------------------------

class ProcessingLog(BaseModel):
    """Audit record for a single webhook processing run."""

    id: UUID = Field(default_factory=uuid4)
    webhook_id: UUID
    source: FormSource
    status: ProcessingStatus = ProcessingStatus.RECEIVED
    steps: list[dict[str, Any]] = Field(default_factory=list)
    error_message: str | None = None
    hubspot_contact_id: str | None = None
    airtable_record_id: str | None = None
    duration_ms: float | None = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    def add_step(self, name: str, detail: str = "", success: bool = True) -> None:
        """Append a processing step to the log."""
        self.steps.append(
            {"name": name, "detail": detail, "success": success, "ts": datetime.utcnow().isoformat()}
        )


# ---------------------------------------------------------------------------
# Contact record
# ---------------------------------------------------------------------------

class ContactRecord(BaseModel):
    """Unified contact representation across CRMs."""

    id: UUID = Field(default_factory=uuid4)
    email: EmailStr | None = None
    first_name: str | None = None
    last_name: str | None = None
    phone: str | None = None
    company: str | None = None
    source: FormSource | None = None
    custom_fields: dict[str, Any] = Field(default_factory=dict)
    hubspot_id: str | None = None
    airtable_id: str | None = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
