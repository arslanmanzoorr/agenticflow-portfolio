"""API response models."""

from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field

from src.models.webhook import FieldMapping, ProcessingLog


class APIResponse(BaseModel):
    """Generic wrapper for all API responses."""

    success: bool = True
    message: str = ""
    data: Any = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class WebhookResponse(BaseModel):
    """Returned after a webhook is received and processed."""

    webhook_id: UUID
    status: str
    hubspot_contact_id: str | None = None
    airtable_record_id: str | None = None
    errors: list[str] = Field(default_factory=list)


class HealthResponse(BaseModel):
    """Health-check payload."""

    status: str = "healthy"
    version: str = ""
    uptime_seconds: float = 0.0
    services: dict[str, str] = Field(default_factory=dict)


class MappingListResponse(BaseModel):
    """List of field mappings."""

    mappings: list[FieldMapping] = Field(default_factory=list)
    total: int = 0


class LogListResponse(BaseModel):
    """Paginated processing logs."""

    logs: list[ProcessingLog] = Field(default_factory=list)
    total: int = 0
    page: int = 1
    page_size: int = 50
