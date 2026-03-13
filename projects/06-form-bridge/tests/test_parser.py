"""Tests for the FormBridge universal form-data parser.

Covers Typeform, JotForm, Google Forms, Gravity Forms, and custom JSON
payloads to ensure correct source detection and field extraction.
"""

from __future__ import annotations

import pytest

from src.models.webhook import FormField, FormSource, WebhookPayload
from src.services.parser import detect_source, parse_webhook


# ---------------------------------------------------------------------------
# Fixtures -- sample payloads
# ---------------------------------------------------------------------------


@pytest.fixture
def typeform_payload() -> dict:
    """Minimal Typeform webhook payload."""
    return {
        "form_response": {
            "form_id": "abc123",
            "submitted_at": "2024-01-15T10:30:00Z",
            "definition": {
                "fields": [
                    {"id": "f1", "ref": "name_ref", "title": "Full Name"},
                    {"id": "f2", "ref": "email_ref", "title": "Email"},
                    {"id": "f3", "ref": "company_ref", "title": "Company"},
                ],
            },
            "answers": [
                {"field": {"ref": "name_ref"}, "type": "text", "text": "Jane Doe"},
                {"field": {"ref": "email_ref"}, "type": "email", "email": "jane@example.com"},
                {"field": {"ref": "company_ref"}, "type": "text", "text": "Acme Inc"},
            ],
        }
    }


@pytest.fixture
def jotform_payload() -> dict:
    """Minimal JotForm webhook payload."""
    return {
        "formID": "123456789",
        "submissionID": "sub_001",
        "rawRequest": '{"q1_fullName": "John Smith", "q2_email": "john@example.com", "q3_phone": "+1234567890"}',
    }


@pytest.fixture
def jotform_payload_flat() -> dict:
    """JotForm payload without rawRequest wrapper."""
    return {
        "formID": "123456789",
        "submissionID": "sub_002",
        "q1_fullName": "Alice Johnson",
        "q2_email": "alice@example.com",
        "q3_companyName": "TechCorp",
    }


@pytest.fixture
def google_forms_payload() -> dict:
    """Google Forms webhook payload (via Apps Script)."""
    return {
        "response": {
            "responseId": "resp_abc",
            "respondentEmail": "bob@example.com",
            "answers": [
                {
                    "questionId": "q1",
                    "title": "Your Name",
                    "textAnswers": {"answers": [{"value": "Bob Williams"}]},
                },
                {
                    "questionId": "q2",
                    "title": "Email Address",
                    "textAnswers": {"answers": [{"value": "bob@example.com"}]},
                },
                {
                    "questionId": "q3",
                    "title": "Phone Number",
                    "textAnswers": {"answers": [{"value": "555-0123"}]},
                },
            ],
        }
    }


@pytest.fixture
def gravity_forms_payload() -> dict:
    """Gravity Forms webhook payload."""
    return {
        "form": {
            "id": 1,
            "fields": [
                {"id": 1, "label": "Name", "type": "name", "inputs": [
                    {"id": "1.3", "label": "First Name"},
                    {"id": "1.6", "label": "Last Name"},
                ]},
                {"id": 2, "label": "Email", "type": "email"},
                {"id": 3, "label": "Phone", "type": "phone"},
            ],
        },
        "entry": {
            "id": "42",
            "form_id": "1",
            "1.3": "Carlos",
            "1.6": "Rivera",
            "2": "carlos@example.com",
            "3": "555-9876",
            "date_created": "2024-01-15 12:00:00",
            "source_url": "https://example.com/contact",
            "ip": "127.0.0.1",
        },
    }


@pytest.fixture
def custom_payload() -> dict:
    """Arbitrary custom JSON payload."""
    return {
        "first_name": "Diana",
        "last_name": "Prince",
        "email": "diana@example.com",
        "phone": "555-0000",
        "company": "Wayne Enterprises",
        "message": "I'd like to learn more about your services.",
    }


# ---------------------------------------------------------------------------
# Source detection tests
# ---------------------------------------------------------------------------


class TestDetectSource:
    """Tests for the detect_source function."""

    def test_detects_typeform(self, typeform_payload: dict) -> None:
        assert detect_source(typeform_payload) == FormSource.TYPEFORM

    def test_detects_jotform(self, jotform_payload: dict) -> None:
        assert detect_source(jotform_payload) == FormSource.JOTFORM

    def test_detects_jotform_flat(self, jotform_payload_flat: dict) -> None:
        assert detect_source(jotform_payload_flat) == FormSource.JOTFORM

    def test_detects_google_forms(self, google_forms_payload: dict) -> None:
        assert detect_source(google_forms_payload) == FormSource.GOOGLE_FORMS

    def test_detects_gravity_forms(self, gravity_forms_payload: dict) -> None:
        assert detect_source(gravity_forms_payload) == FormSource.GRAVITY_FORMS

    def test_detects_custom(self, custom_payload: dict) -> None:
        assert detect_source(custom_payload) == FormSource.CUSTOM

    def test_empty_payload_is_custom(self) -> None:
        assert detect_source({}) == FormSource.CUSTOM


# ---------------------------------------------------------------------------
# Typeform parser tests
# ---------------------------------------------------------------------------


class TestTypeformParser:
    """Tests for parsing Typeform webhooks."""

    def test_parses_all_fields(self, typeform_payload: dict) -> None:
        result = parse_webhook(typeform_payload)
        assert result.source == FormSource.TYPEFORM
        assert len(result.fields) == 3

    def test_extracts_text_values(self, typeform_payload: dict) -> None:
        result = parse_webhook(typeform_payload)
        name_field = next(f for f in result.fields if f.key == "name_ref")
        assert name_field.value == "Jane Doe"
        assert name_field.label == "Full Name"

    def test_extracts_email_type(self, typeform_payload: dict) -> None:
        result = parse_webhook(typeform_payload)
        email_field = next(f for f in result.fields if f.key == "email_ref")
        assert email_field.value == "jane@example.com"
        assert email_field.field_type == "email"

    def test_metadata_includes_form_id(self, typeform_payload: dict) -> None:
        result = parse_webhook(typeform_payload)
        assert result.metadata.get("form_id") == "abc123"
        assert result.metadata.get("submitted_at") == "2024-01-15T10:30:00Z"

    def test_source_hint_overrides_detection(self, typeform_payload: dict) -> None:
        result = parse_webhook(typeform_payload, source_hint="typeform")
        assert result.source == FormSource.TYPEFORM


# ---------------------------------------------------------------------------
# JotForm parser tests
# ---------------------------------------------------------------------------


class TestJotFormParser:
    """Tests for parsing JotForm webhooks."""

    def test_parses_raw_request(self, jotform_payload: dict) -> None:
        result = parse_webhook(jotform_payload)
        assert result.source == FormSource.JOTFORM
        assert len(result.fields) == 3

    def test_extracts_fields_from_raw_request(self, jotform_payload: dict) -> None:
        result = parse_webhook(jotform_payload)
        field_keys = {f.key for f in result.fields}
        assert "q1_fullName" in field_keys
        assert "q2_email" in field_keys

    def test_email_field_type_detected(self, jotform_payload: dict) -> None:
        result = parse_webhook(jotform_payload)
        email_field = next(f for f in result.fields if "email" in f.key.lower())
        assert email_field.field_type == "email"

    def test_flat_jotform_payload(self, jotform_payload_flat: dict) -> None:
        result = parse_webhook(jotform_payload_flat)
        assert result.source == FormSource.JOTFORM
        # Should skip formID and submissionID
        field_keys = {f.key for f in result.fields}
        assert "formID" not in field_keys
        assert "submissionID" not in field_keys

    def test_metadata_includes_form_id(self, jotform_payload: dict) -> None:
        result = parse_webhook(jotform_payload)
        assert result.metadata.get("form_id") == "123456789"


# ---------------------------------------------------------------------------
# Google Forms parser tests
# ---------------------------------------------------------------------------


class TestGoogleFormsParser:
    """Tests for parsing Google Forms webhooks."""

    def test_parses_answers(self, google_forms_payload: dict) -> None:
        result = parse_webhook(google_forms_payload)
        assert result.source == FormSource.GOOGLE_FORMS
        assert len(result.fields) == 3

    def test_extracts_text_answer_values(self, google_forms_payload: dict) -> None:
        result = parse_webhook(google_forms_payload)
        name_field = next(f for f in result.fields if f.label == "Your Name")
        assert name_field.value == "Bob Williams"

    def test_detects_email_field_type(self, google_forms_payload: dict) -> None:
        result = parse_webhook(google_forms_payload)
        email_field = next(f for f in result.fields if "email" in f.label.lower())
        assert email_field.field_type == "email"

    def test_detects_phone_field_type(self, google_forms_payload: dict) -> None:
        result = parse_webhook(google_forms_payload)
        phone_field = next(f for f in result.fields if "phone" in f.label.lower())
        assert phone_field.field_type == "phone"


# ---------------------------------------------------------------------------
# Gravity Forms parser tests
# ---------------------------------------------------------------------------


class TestGravityFormsParser:
    """Tests for parsing Gravity Forms webhooks."""

    def test_parses_entry_fields(self, gravity_forms_payload: dict) -> None:
        result = parse_webhook(gravity_forms_payload)
        assert result.source == FormSource.GRAVITY_FORMS
        assert len(result.fields) > 0

    def test_skips_metadata_fields(self, gravity_forms_payload: dict) -> None:
        result = parse_webhook(gravity_forms_payload)
        field_keys = {f.key for f in result.fields}
        assert "date_created" not in field_keys
        assert "source_url" not in field_keys
        assert "ip" not in field_keys

    def test_uses_labels_from_form_definition(self, gravity_forms_payload: dict) -> None:
        result = parse_webhook(gravity_forms_payload)
        # Sub-field 1.3 should get label "First Name" from the form definition
        first_name = next((f for f in result.fields if f.key == "1.3"), None)
        if first_name:
            assert first_name.label == "First Name"

    def test_extracts_email_value(self, gravity_forms_payload: dict) -> None:
        result = parse_webhook(gravity_forms_payload)
        email_field = next((f for f in result.fields if f.key == "2"), None)
        assert email_field is not None
        assert email_field.value == "carlos@example.com"


# ---------------------------------------------------------------------------
# Custom payload parser tests
# ---------------------------------------------------------------------------


class TestCustomParser:
    """Tests for parsing arbitrary JSON payloads."""

    def test_parses_flat_json(self, custom_payload: dict) -> None:
        result = parse_webhook(custom_payload)
        assert result.source == FormSource.CUSTOM
        assert len(result.fields) == 6

    def test_detects_email_field_type(self, custom_payload: dict) -> None:
        result = parse_webhook(custom_payload)
        email_field = next(f for f in result.fields if f.key == "email")
        assert email_field.field_type == "email"
        assert email_field.value == "diana@example.com"

    def test_detects_phone_field_type(self, custom_payload: dict) -> None:
        result = parse_webhook(custom_payload)
        phone_field = next(f for f in result.fields if f.key == "phone")
        assert phone_field.field_type == "phone"

    def test_handles_nested_payload(self) -> None:
        nested = {
            "contact": {
                "email": "nested@example.com",
                "name": "Nested User",
            },
            "message": "Hello",
        }
        result = parse_webhook(nested)
        field_keys = {f.key for f in result.fields}
        assert "contact.email" in field_keys
        assert "contact.name" in field_keys
        assert "message" in field_keys

    def test_source_hint_forces_custom(self, typeform_payload: dict) -> None:
        result = parse_webhook(typeform_payload, source_hint="custom")
        assert result.source == FormSource.CUSTOM

    def test_invalid_source_hint_falls_back(self, custom_payload: dict) -> None:
        result = parse_webhook(custom_payload, source_hint="nonexistent_provider")
        assert result.source == FormSource.CUSTOM

    def test_empty_payload(self) -> None:
        result = parse_webhook({})
        assert result.source == FormSource.CUSTOM
        assert len(result.fields) == 0


# ---------------------------------------------------------------------------
# WebhookPayload model tests
# ---------------------------------------------------------------------------


class TestWebhookPayload:
    """Tests for the WebhookPayload model produced by the parser."""

    def test_has_unique_id(self, typeform_payload: dict) -> None:
        r1 = parse_webhook(typeform_payload)
        r2 = parse_webhook(typeform_payload)
        assert r1.id != r2.id

    def test_stores_raw_payload(self, typeform_payload: dict) -> None:
        result = parse_webhook(typeform_payload)
        assert result.raw_payload == typeform_payload

    def test_has_received_at_timestamp(self, custom_payload: dict) -> None:
        result = parse_webhook(custom_payload)
        assert result.received_at is not None
