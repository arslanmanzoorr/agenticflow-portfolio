"""Universal form-data parser.

Normalises payloads from Typeform, JotForm, Google Forms, Gravity Forms,
and arbitrary JSON into a unified list of ``FormField`` objects.
"""

from __future__ import annotations

import logging
from typing import Any

from src.models.webhook import FormField, FormSource, WebhookPayload

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Source detection
# ---------------------------------------------------------------------------

def detect_source(payload: dict[str, Any]) -> FormSource:
    """Heuristically detect which form provider sent the payload."""

    # Typeform: top-level "form_response" key
    if "form_response" in payload:
        return FormSource.TYPEFORM

    # JotForm: top-level "formID" or "rawRequest"
    if "formID" in payload or "rawRequest" in payload:
        return FormSource.JOTFORM

    # Google Forms: has "response" with "answers" list, or "form" + "responses"
    if "response" in payload and isinstance(payload["response"], dict):
        resp = payload["response"]
        if "answers" in resp or "respondentEmail" in resp:
            return FormSource.GOOGLE_FORMS

    # Gravity Forms: has "form" dict with "id" and "entries" or "body" with "entry"
    if ("form" in payload and "entry" in payload) or "gform_unique_id" in payload:
        return FormSource.GRAVITY_FORMS

    return FormSource.CUSTOM


# ---------------------------------------------------------------------------
# Provider-specific parsers
# ---------------------------------------------------------------------------

def _parse_typeform(payload: dict[str, Any]) -> list[FormField]:
    """Parse a Typeform webhook payload."""
    fields: list[FormField] = []
    form_response = payload.get("form_response", {})
    answers = form_response.get("answers", [])
    definition = form_response.get("definition", {})

    # Build a map of field ref -> label from the definition
    field_labels: dict[str, str] = {}
    for field_def in definition.get("fields", []):
        ref = field_def.get("ref", field_def.get("id", ""))
        field_labels[ref] = field_def.get("title", "")

    for answer in answers:
        field_ref = answer.get("field", {}).get("ref", answer.get("field", {}).get("id", ""))
        field_type = answer.get("type", "text")

        # Extract value based on answer type
        value: Any = None
        if field_type == "text":
            value = answer.get("text")
        elif field_type == "email":
            value = answer.get("email")
        elif field_type == "phone_number":
            value = answer.get("phone_number")
        elif field_type == "number":
            value = answer.get("number")
        elif field_type == "boolean":
            value = answer.get("boolean")
        elif field_type == "date":
            value = answer.get("date")
        elif field_type == "choice":
            choice = answer.get("choice", {})
            value = choice.get("label", choice.get("other", ""))
        elif field_type == "choices":
            choices = answer.get("choices", {})
            value = choices.get("labels", [])
        elif field_type == "url":
            value = answer.get("url")
        else:
            value = answer.get(field_type)

        fields.append(
            FormField(
                key=field_ref,
                label=field_labels.get(field_ref, field_ref),
                value=value,
                field_type=field_type,
            )
        )

    return fields


def _parse_jotform(payload: dict[str, Any]) -> list[FormField]:
    """Parse a JotForm webhook payload."""
    fields: list[FormField] = []

    # JotForm sends either a flat dict or nested "rawRequest"
    raw = payload
    if "rawRequest" in payload:
        import json

        try:
            raw = json.loads(payload["rawRequest"]) if isinstance(payload["rawRequest"], str) else payload["rawRequest"]
        except (json.JSONDecodeError, TypeError):
            raw = payload

    skip_keys = {"formID", "submissionID", "rawRequest", "pretty", "type", "event_id"}

    for key, value in raw.items():
        if key in skip_keys:
            continue

        # JotForm uses q{N}_{name} naming pattern
        label = key
        field_type = "text"

        if isinstance(value, dict):
            # Compound field (name, address)
            combined_parts = [str(v) for v in value.values() if v]
            value = " ".join(combined_parts) if combined_parts else ""

        if "email" in key.lower():
            field_type = "email"
        elif "phone" in key.lower():
            field_type = "phone"

        fields.append(FormField(key=key, label=label, value=value, field_type=field_type))

    return fields


def _parse_google_forms(payload: dict[str, Any]) -> list[FormField]:
    """Parse a Google Forms webhook payload (via Apps Script or add-on)."""
    fields: list[FormField] = []
    response = payload.get("response", payload)

    answers = response.get("answers", [])
    for answer in answers:
        question_id = answer.get("questionId", answer.get("id", ""))
        title = answer.get("title", answer.get("question", question_id))

        # Google Forms answers can be text or list
        text_answers = answer.get("textAnswers", {})
        answer_list = text_answers.get("answers", [])
        if answer_list:
            value = answer_list[0].get("value", "") if len(answer_list) == 1 else [a.get("value", "") for a in answer_list]
        else:
            value = answer.get("response", answer.get("answer", ""))

        field_type = "text"
        if "email" in title.lower():
            field_type = "email"
        elif "phone" in title.lower():
            field_type = "phone"
        elif "date" in title.lower():
            field_type = "date"

        fields.append(FormField(key=question_id, label=title, value=value, field_type=field_type))

    # Also handle flat key/value response format
    if not answers and isinstance(response, dict):
        skip = {"respondentEmail", "responseId", "timestamp", "formId"}
        for key, value in response.items():
            if key in skip:
                continue
            fields.append(FormField(key=key, label=key, value=value, field_type="text"))

    return fields


def _parse_gravity_forms(payload: dict[str, Any]) -> list[FormField]:
    """Parse a Gravity Forms webhook payload."""
    fields: list[FormField] = []
    entry = payload.get("entry", payload.get("body", {}).get("entry", {}))
    form_def = payload.get("form", {})

    # Build a field ID -> label map from form definition
    field_map: dict[str, dict[str, str]] = {}
    for f in form_def.get("fields", []):
        fid = str(f.get("id", ""))
        field_map[fid] = {"label": f.get("label", ""), "type": f.get("type", "text")}
        # Sub-fields (name, address components)
        for inp in f.get("inputs", []):
            sub_id = str(inp.get("id", ""))
            field_map[sub_id] = {"label": inp.get("label", ""), "type": f.get("type", "text")}

    skip_keys = {
        "id", "form_id", "post_id", "date_created", "date_updated",
        "source_url", "ip", "user_agent", "status", "created_by",
        "currency", "payment_status", "payment_amount", "is_starred",
        "is_read", "entry_id",
    }

    for key, value in entry.items():
        if key in skip_keys or not value:
            continue

        meta = field_map.get(key, {})
        label = meta.get("label", key)
        field_type = meta.get("type", "text")

        fields.append(FormField(key=key, label=label, value=value, field_type=field_type))

    return fields


def _parse_custom(payload: dict[str, Any]) -> list[FormField]:
    """Parse an arbitrary JSON payload into form fields."""
    fields: list[FormField] = []

    def _flatten(data: dict[str, Any], prefix: str = "") -> None:
        for key, value in data.items():
            full_key = f"{prefix}.{key}" if prefix else key
            if isinstance(value, dict):
                _flatten(value, full_key)
            else:
                field_type = "text"
                key_lower = key.lower()
                if "email" in key_lower:
                    field_type = "email"
                elif "phone" in key_lower or "mobile" in key_lower:
                    field_type = "phone"
                elif "date" in key_lower:
                    field_type = "date"

                fields.append(FormField(key=full_key, label=key, value=value, field_type=field_type))

    _flatten(payload)
    return fields


# ---------------------------------------------------------------------------
# Dispatcher table
# ---------------------------------------------------------------------------

_PARSERS: dict[FormSource, Any] = {
    FormSource.TYPEFORM: _parse_typeform,
    FormSource.JOTFORM: _parse_jotform,
    FormSource.GOOGLE_FORMS: _parse_google_forms,
    FormSource.GRAVITY_FORMS: _parse_gravity_forms,
    FormSource.CUSTOM: _parse_custom,
}


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def parse_webhook(raw_payload: dict[str, Any], source_hint: str | None = None) -> WebhookPayload:
    """Parse a raw webhook body into a normalised ``WebhookPayload``.

    Parameters
    ----------
    raw_payload:
        The JSON body received from the form provider.
    source_hint:
        Optional explicit source (e.g. ``"typeform"``).  When *None* the
        source is auto-detected from the payload structure.

    Returns
    -------
    WebhookPayload
        Normalised payload with extracted form fields.
    """
    if source_hint:
        try:
            source = FormSource(source_hint.lower())
        except ValueError:
            logger.warning("Unknown source hint '%s', falling back to auto-detect", source_hint)
            source = detect_source(raw_payload)
    else:
        source = detect_source(raw_payload)

    parser_fn = _PARSERS.get(source, _parse_custom)

    try:
        fields = parser_fn(raw_payload)
    except Exception:
        logger.exception("Parser for %s failed, falling back to custom parser", source.value)
        fields = _parse_custom(raw_payload)

    metadata: dict[str, Any] = {}
    if source == FormSource.TYPEFORM:
        fr = raw_payload.get("form_response", {})
        metadata["form_id"] = fr.get("form_id", "")
        metadata["submitted_at"] = fr.get("submitted_at", "")
    elif source == FormSource.JOTFORM:
        metadata["form_id"] = raw_payload.get("formID", "")
        metadata["submission_id"] = raw_payload.get("submissionID", "")
    elif source == FormSource.GRAVITY_FORMS:
        metadata["form_id"] = raw_payload.get("form", {}).get("id", "")

    logger.info(
        "Parsed %s webhook: %d fields extracted (source=%s)",
        source.value,
        len(fields),
        source.value,
    )

    return WebhookPayload(
        source=source,
        raw_payload=raw_payload,
        fields=fields,
        metadata=metadata,
    )
