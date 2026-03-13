"""FormBridge API -- FastAPI application.

Universal webhook-to-CRM connector that receives form submissions from
Typeform, JotForm, Google Forms, Gravity Forms, or custom JSON payloads,
normalises the data, syncs to HubSpot CRM and Airtable, and sends Slack
notifications.
"""

from __future__ import annotations

import logging
import time
from contextlib import asynccontextmanager
from typing import Any, AsyncIterator

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware

from src.config import get_settings
from src.models.responses import (
    APIResponse,
    HealthResponse,
    WebhookResponse,
)
from src.models.webhook import (
    ContactRecord,
    FormSource,
    ProcessingLog,
    ProcessingStatus,
    WebhookPayload,
)
from src.services.airtable_client import AirtableClient
from src.services.hubspot_client import HubSpotClient
from src.services.mapper import map_payload
from src.services.parser import parse_webhook
from src.services.slack_notifier import SlackNotifier

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Shared service instances
# ---------------------------------------------------------------------------

_hubspot: HubSpotClient | None = None
_airtable: AirtableClient | None = None
_slack: SlackNotifier | None = None
_start_time: float = 0.0


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    """Initialise and tear down shared service singletons."""
    global _hubspot, _airtable, _slack, _start_time  # noqa: PLW0603

    _hubspot = HubSpotClient()
    _airtable = AirtableClient()
    _slack = SlackNotifier()
    _start_time = time.time()

    logger.info("FormBridge API started")
    yield
    logger.info("FormBridge API shutting down")


# ---------------------------------------------------------------------------
# FastAPI application
# ---------------------------------------------------------------------------

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Universal webhook-to-CRM connector for form submissions",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins or ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Dependency helpers
# ---------------------------------------------------------------------------


def _get_hubspot() -> HubSpotClient:
    if _hubspot is None:
        raise HTTPException(status_code=503, detail="Service not initialised")
    return _hubspot


def _get_airtable() -> AirtableClient:
    if _airtable is None:
        raise HTTPException(status_code=503, detail="Service not initialised")
    return _airtable


def _get_slack() -> SlackNotifier:
    if _slack is None:
        raise HTTPException(status_code=503, detail="Service not initialised")
    return _slack


# ---------------------------------------------------------------------------
# Core processing pipeline
# ---------------------------------------------------------------------------


async def _process_submission(
    raw_payload: dict[str, Any],
    source_hint: str | None = None,
) -> WebhookResponse:
    """Run the full parse -> map -> sync pipeline for a submission.

    Steps:
    1. Parse raw payload into normalised WebhookPayload
    2. Map fields to a ContactRecord
    3. Upsert contact in HubSpot
    4. Log submission and upsert contact in Airtable
    5. Send Slack notification
    """
    hubspot = _get_hubspot()
    airtable = _get_airtable()
    slack = _get_slack()

    log = ProcessingLog(
        webhook_id=None,  # type: ignore[arg-type] -- assigned after parsing
        source=FormSource.CUSTOM,
    )

    errors: list[str] = []
    hubspot_contact_id: str | None = None
    airtable_record_id: str | None = None

    try:
        # 1. Parse
        payload: WebhookPayload = parse_webhook(raw_payload, source_hint=source_hint)
        log.webhook_id = payload.id
        log.source = payload.source
        log.status = ProcessingStatus.PARSED
        log.add_step("parse", f"Extracted {len(payload.fields)} fields from {payload.source.value}")

        # 2. Map
        contact: ContactRecord = map_payload(payload)
        log.status = ProcessingStatus.MAPPED
        log.add_step("map", f"Mapped to contact: {contact.email or 'no email'}")

        # 3. HubSpot upsert
        try:
            hubspot_contact_id = await hubspot.upsert_contact(contact)
            if hubspot_contact_id:
                log.hubspot_contact_id = hubspot_contact_id
                log.add_step("hubspot", f"Upserted contact {hubspot_contact_id}")
            else:
                log.add_step("hubspot", "Skipped -- no email provided", success=False)
        except Exception as exc:
            err_msg = f"HubSpot sync failed: {exc}"
            logger.warning(err_msg)
            errors.append(err_msg)
            log.add_step("hubspot", err_msg, success=False)

        # 4. Airtable log + upsert
        try:
            airtable_record_id = await airtable.log_submission(payload, contact)
            log.airtable_record_id = airtable_record_id
            log.add_step("airtable_submission", f"Logged submission {airtable_record_id}")

            await airtable.upsert_contact(contact)
            log.add_step("airtable_contact", "Contact upserted")
        except Exception as exc:
            err_msg = f"Airtable sync failed: {exc}"
            logger.warning(err_msg)
            errors.append(err_msg)
            log.add_step("airtable", err_msg, success=False)

        # 5. Slack notification
        try:
            await slack.notify_submission(payload, contact, hubspot_contact_id)
            log.add_step("slack", "Notification sent")
        except Exception as exc:
            err_msg = f"Slack notification failed: {exc}"
            logger.warning(err_msg)
            errors.append(err_msg)
            log.add_step("slack", err_msg, success=False)

        log.status = ProcessingStatus.SYNCED if not errors else ProcessingStatus.PARSED

    except Exception as exc:
        logger.exception("Webhook processing pipeline failed")
        log.status = ProcessingStatus.FAILED
        log.error_message = str(exc)
        errors.append(str(exc))

    return WebhookResponse(
        webhook_id=log.webhook_id,
        status=log.status.value,
        hubspot_contact_id=hubspot_contact_id,
        airtable_record_id=airtable_record_id,
        errors=errors,
    )


# ---------------------------------------------------------------------------
# GET /health
# ---------------------------------------------------------------------------


@app.get("/health", response_model=HealthResponse, tags=["system"])
async def health_check() -> HealthResponse:
    """Return service health status."""
    return HealthResponse(
        status="healthy",
        version=settings.app_version,
        uptime_seconds=round(time.time() - _start_time, 2) if _start_time else 0.0,
        services={
            "hubspot": "configured" if settings.hubspot_api_key else "not configured",
            "airtable": "configured" if settings.airtable_api_key else "not configured",
            "slack": "configured" if settings.slack_webhook_url else "not configured",
        },
    )


# ---------------------------------------------------------------------------
# POST /webhook/{source} -- receive webhook with explicit source
# ---------------------------------------------------------------------------


@app.post("/webhook/{source}", response_model=WebhookResponse, tags=["webhooks"])
async def receive_webhook_with_source(source: str, request: Request) -> WebhookResponse:
    """Receive a form submission webhook with an explicit source provider.

    Supported sources: typeform, jotform, google_forms, gravity_forms, custom.
    """
    valid_sources = {s.value for s in FormSource}
    if source.lower() not in valid_sources:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown source '{source}'. Valid sources: {', '.join(sorted(valid_sources))}",
        )

    try:
        raw_payload = await request.json()
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Invalid JSON body: {exc}") from exc

    return await _process_submission(raw_payload, source_hint=source)


# ---------------------------------------------------------------------------
# POST /webhook -- auto-detect source
# ---------------------------------------------------------------------------


@app.post("/webhook", response_model=WebhookResponse, tags=["webhooks"])
async def receive_webhook_auto(request: Request) -> WebhookResponse:
    """Receive a form submission webhook and auto-detect the source provider.

    The parser examines the payload structure to determine whether it came
    from Typeform, JotForm, Google Forms, Gravity Forms, or a custom source.
    """
    try:
        raw_payload = await request.json()
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Invalid JSON body: {exc}") from exc

    return await _process_submission(raw_payload, source_hint=None)


# ---------------------------------------------------------------------------
# GET /submissions -- list processed submissions
# ---------------------------------------------------------------------------


@app.get("/submissions", response_model=APIResponse, tags=["submissions"])
async def list_submissions(
    source: str | None = Query(default=None, description="Filter by form source"),
    limit: int = Query(default=50, ge=1, le=200, description="Maximum results"),
) -> APIResponse:
    """List all processed form submissions from Airtable."""
    airtable = _get_airtable()

    try:
        # Query Airtable submissions table
        async with airtable._client() as client:
            params: dict[str, str] = {"maxRecords": str(limit)}
            if source:
                params["filterByFormula"] = f"{{Source}} = '{source}'"

            resp = await client.get(f"/{airtable._submissions_table}", params=params)

            if resp.status_code != 200:
                raise HTTPException(status_code=502, detail="Airtable query failed")

            records = resp.json().get("records", [])
            submissions = [
                {
                    "id": r["id"],
                    "fields": r["fields"],
                }
                for r in records
            ]

        return APIResponse(
            success=True,
            message=f"Found {len(submissions)} submission(s)",
            data=submissions,
        )

    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Failed to list submissions")
        raise HTTPException(status_code=500, detail=str(exc)) from exc


# ---------------------------------------------------------------------------
# GET /submissions/{submission_id} -- get submission details
# ---------------------------------------------------------------------------


@app.get("/submissions/{submission_id}", response_model=APIResponse, tags=["submissions"])
async def get_submission(submission_id: str) -> APIResponse:
    """Get details of a specific processed submission by its Airtable record ID."""
    airtable = _get_airtable()

    try:
        async with airtable._client() as client:
            resp = await client.get(f"/{airtable._submissions_table}/{submission_id}")

            if resp.status_code == 404:
                raise HTTPException(
                    status_code=404,
                    detail=f"Submission '{submission_id}' not found",
                )

            if resp.status_code != 200:
                raise HTTPException(status_code=502, detail="Airtable query failed")

            record = resp.json()

        return APIResponse(
            success=True,
            message="Submission found",
            data={"id": record["id"], "fields": record["fields"]},
        )

    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Failed to get submission")
        raise HTTPException(status_code=500, detail=str(exc)) from exc
