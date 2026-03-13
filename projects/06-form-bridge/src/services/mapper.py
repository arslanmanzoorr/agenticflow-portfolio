"""Field mapping engine.

Maps normalised form fields to CRM fields using configurable mapping rules,
with support for value transformations.
"""

from __future__ import annotations

import logging
import re
from datetime import datetime
from typing import Any
from uuid import UUID

from src.models.webhook import (
    ContactRecord,
    FieldMapping,
    FormSource,
    TransformationType,
    WebhookPayload,
)

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# In-memory mapping store (swap for a DB in production)
# ---------------------------------------------------------------------------

_mappings: dict[UUID, FieldMapping] = {}

# ---------------------------------------------------------------------------
# Default mappings applied when no explicit mapping is configured
# ---------------------------------------------------------------------------

_DEFAULT_FIELD_MAP: dict[str, str] = {
    "email": "email",
    "e-mail": "email",
    "first_name": "first_name",
    "firstname": "first_name",
    "first name": "first_name",
    "last_name": "last_name",
    "lastname": "last_name",
    "last name": "last_name",
    "name": "first_name",
    "full_name": "first_name",
    "phone": "phone",
    "phone_number": "phone",
    "telephone": "phone",
    "mobile": "phone",
    "company": "company",
    "organisation": "company",
    "organization": "company",
    "company_name": "company",
}


# ---------------------------------------------------------------------------
# Transformations
# ---------------------------------------------------------------------------

def _apply_transformation(value: Any, transformation: TransformationType) -> Any:
    """Apply a transformation to a field value."""
    if value is None:
        return value

    str_value = str(value)

    match transformation:
        case TransformationType.CAPITALIZE:
            return str_value.capitalize()
        case TransformationType.LOWERCASE:
            return str_value.lower()
        case TransformationType.UPPERCASE:
            return str_value.upper()
        case TransformationType.TITLE_CASE:
            return str_value.title()
        case TransformationType.STRIP:
            return str_value.strip()
        case TransformationType.FORMAT_PHONE:
            return _format_phone(str_value)
        case TransformationType.PARSE_DATE:
            return _parse_date(str_value)
        case TransformationType.NONE:
            return value
        case _:
            return value


def _format_phone(raw: str) -> str:
    """Normalise a phone number to E.164-ish format."""
    digits = re.sub(r"[^\d+]", "", raw)
    if not digits:
        return raw

    # Already has country code
    if digits.startswith("+"):
        return digits

    # US/CA 10-digit
    if len(digits) == 10:
        return f"+1{digits}"

    # 11-digit starting with 1
    if len(digits) == 11 and digits.startswith("1"):
        return f"+{digits}"

    return digits


def _parse_date(raw: str) -> str:
    """Try common date formats and return ISO-8601."""
    formats = [
        "%Y-%m-%d",
        "%m/%d/%Y",
        "%d/%m/%Y",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%dT%H:%M:%SZ",
        "%B %d, %Y",
        "%b %d, %Y",
        "%d %B %Y",
        "%d-%m-%Y",
    ]
    for fmt in formats:
        try:
            return datetime.strptime(raw.strip(), fmt).date().isoformat()
        except ValueError:
            continue
    return raw


# ---------------------------------------------------------------------------
# CRUD helpers for mappings
# ---------------------------------------------------------------------------

def list_mappings() -> list[FieldMapping]:
    """Return all configured field mappings."""
    return list(_mappings.values())


def add_mapping(mapping: FieldMapping) -> FieldMapping:
    """Store a new field mapping."""
    _mappings[mapping.id] = mapping
    logger.info("Added mapping %s: %s -> %s", mapping.id, mapping.source_field, mapping.destination_field)
    return mapping


def remove_mapping(mapping_id: UUID) -> bool:
    """Remove a field mapping. Returns ``True`` if found and removed."""
    return _mappings.pop(mapping_id, None) is not None


def clear_mappings() -> None:
    """Remove all mappings (useful for testing)."""
    _mappings.clear()


# ---------------------------------------------------------------------------
# Core mapping logic
# ---------------------------------------------------------------------------

def map_payload(payload: WebhookPayload) -> ContactRecord:
    """Map a parsed webhook payload to a ``ContactRecord``.

    1. Looks for explicit mappings that match the payload source.
    2. Falls back to default field-name matching for unmapped fields.
    3. Applies configured transformations.
    """
    contact_data: dict[str, Any] = {"source": payload.source, "custom_fields": {}}

    # Gather explicit mappings for this source
    source_mappings = {
        m.source_field: m
        for m in _mappings.values()
        if m.source in (payload.source, FormSource.CUSTOM)
    }

    crm_fields = {"email", "first_name", "last_name", "phone", "company"}

    for field in payload.fields:
        dest_field: str | None = None
        transformation = TransformationType.NONE
        value = field.value

        # 1. Explicit mapping takes priority
        if field.key in source_mappings:
            mapping = source_mappings[field.key]
            dest_field = mapping.destination_field
            transformation = mapping.transformation
            if value is None and mapping.default_value is not None:
                value = mapping.default_value
        elif field.label and field.label.lower() in source_mappings:
            mapping = source_mappings[field.label.lower()]
            dest_field = mapping.destination_field
            transformation = mapping.transformation
            if value is None and mapping.default_value is not None:
                value = mapping.default_value
        else:
            # 2. Default mapping by key name
            norm_key = field.key.lower().replace("-", "_").replace(" ", "_").strip("_")
            dest_field = _DEFAULT_FIELD_MAP.get(norm_key)

            # Also try the label
            if not dest_field and field.label:
                norm_label = field.label.lower().replace("-", "_").replace(" ", "_").strip("_")
                dest_field = _DEFAULT_FIELD_MAP.get(norm_label)

            # Infer from field_type
            if not dest_field:
                if field.field_type == "email":
                    dest_field = "email"
                elif field.field_type == "phone":
                    dest_field = "phone"
                    transformation = TransformationType.FORMAT_PHONE

        # Apply transformation
        value = _apply_transformation(value, transformation)

        if dest_field and dest_field in crm_fields:
            contact_data[dest_field] = value
        elif dest_field:
            contact_data["custom_fields"][dest_field] = value
        else:
            # Unmapped fields go into custom_fields
            contact_data["custom_fields"][field.key] = value

    # Handle combined "name" -> split into first/last
    if "first_name" in contact_data and "last_name" not in contact_data:
        name_val = str(contact_data["first_name"]).strip()
        parts = name_val.split(maxsplit=1)
        if len(parts) == 2:
            contact_data["first_name"] = parts[0]
            contact_data["last_name"] = parts[1]

    logger.info(
        "Mapped payload %s to contact: email=%s, name=%s %s",
        payload.id,
        contact_data.get("email", "n/a"),
        contact_data.get("first_name", ""),
        contact_data.get("last_name", ""),
    )

    return ContactRecord(**contact_data)
