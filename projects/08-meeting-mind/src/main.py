"""MeetingMind - AI-powered meeting notes automation system."""

import logging
import shutil
import uuid
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any, AsyncIterator

from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware

from src.config import get_settings
from src.models.meeting import (
    ActionItem,
    ActionItemsRequest,
    MeetingRecord,
    ShareRequest,
    SummarizeRequest,
    Summary,
    Transcript,
    TranscribeResponse,
)
from src.services.action_extractor import ActionExtractorService, ActionExtractionError
from src.services.airtable_client import AirtableClient, AirtableError
from src.services.notifier import NotifierService, NotificationError
from src.services.summarizer import SummarizerService, SummarizationError
from src.services.transcriber import TranscriberService, TranscriptionError

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Application lifespan handler for startup and shutdown events."""
    settings = get_settings()
    settings.upload_path  # ensure upload directory exists
    logger.info("MeetingMind starting up (env=%s)", settings.app_env)
    yield
    logger.info("MeetingMind shutting down...")


app = FastAPI(
    title="MeetingMind",
    description=(
        "AI-powered meeting notes automation. Upload audio recordings to get "
        "transcriptions, summaries, action items, and share results via "
        "Slack or email."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Health
# ---------------------------------------------------------------------------


@app.get("/", tags=["health"])
async def root() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "healthy", "service": "meeting-mind"}


@app.get("/health", tags=["health"])
async def health_check() -> dict[str, str]:
    """Detailed health check."""
    return {"status": "healthy", "service": "meeting-mind", "version": "1.0.0"}


# ---------------------------------------------------------------------------
# Transcription
# ---------------------------------------------------------------------------


@app.post("/transcribe", response_model=TranscribeResponse, tags=["transcription"])
async def transcribe_audio(file: UploadFile = File(...)) -> TranscribeResponse:
    """Upload an audio file and transcribe it using OpenAI Whisper.

    Supported formats: mp3, wav, m4a, mp4, webm, ogg, flac.
    """
    settings = get_settings()
    max_bytes = settings.max_file_size_mb * 1024 * 1024

    if file.size and file.size > max_bytes:
        raise HTTPException(
            status_code=413,
            detail=f"File exceeds {settings.max_file_size_mb} MB limit",
        )

    meeting_id = uuid.uuid4().hex[:12]
    upload_path = settings.upload_path / f"{meeting_id}_{file.filename}"

    try:
        with open(upload_path, "wb") as buf:
            shutil.copyfileobj(file.file, buf)

        transcriber = TranscriberService()
        transcript = await transcriber.transcribe(upload_path)

        # Persist to Airtable (best-effort)
        try:
            airtable = AirtableClient()
            record = MeetingRecord(
                id=meeting_id,
                title=file.filename or "Untitled Meeting",
                audio_filename=file.filename,
                transcript=transcript,
                status="transcribed",
            )
            await airtable.save_meeting(record)
        except Exception as exc:
            logger.warning("Airtable save skipped: %s", exc)

        return TranscribeResponse(meeting_id=meeting_id, transcript=transcript)

    except TranscriptionError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except Exception as exc:
        logger.error("Transcription endpoint error: %s", exc, exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error") from exc


# ---------------------------------------------------------------------------
# Summarization
# ---------------------------------------------------------------------------


@app.post("/summarize", response_model=Summary, tags=["summarization"])
async def summarize_transcript(body: SummarizeRequest) -> Summary:
    """Summarize a transcript using GPT."""
    try:
        summarizer = SummarizerService()
        return await summarizer.summarize(body.transcript_text)
    except SummarizationError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except Exception as exc:
        logger.error("Summarize endpoint error: %s", exc, exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error") from exc


# ---------------------------------------------------------------------------
# Action Items
# ---------------------------------------------------------------------------


@app.post(
    "/action-items", response_model=list[ActionItem], tags=["action-items"]
)
async def extract_action_items(body: ActionItemsRequest) -> list[ActionItem]:
    """Extract action items from a transcript using GPT."""
    try:
        extractor = ActionExtractorService()
        return await extractor.extract(body.transcript_text)
    except ActionExtractionError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except Exception as exc:
        logger.error("Action-items endpoint error: %s", exc, exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error") from exc


# ---------------------------------------------------------------------------
# Meetings CRUD
# ---------------------------------------------------------------------------


@app.get("/meetings", tags=["meetings"])
async def list_meetings() -> list[dict[str, Any]]:
    """List all processed meetings from Airtable."""
    try:
        airtable = AirtableClient()
        return await airtable.list_meetings()
    except AirtableError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@app.get("/meetings/{meeting_id}", tags=["meetings"])
async def get_meeting(meeting_id: str) -> dict[str, Any]:
    """Get meeting details including transcript, summary, and action items."""
    try:
        airtable = AirtableClient()
        meeting = await airtable.get_meeting(meeting_id)
        if not meeting:
            raise HTTPException(status_code=404, detail="Meeting not found")

        action_items = await airtable.get_action_items(meeting_id)
        return {**meeting, "action_items": action_items}

    except AirtableError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


# ---------------------------------------------------------------------------
# Share
# ---------------------------------------------------------------------------


@app.post("/meetings/{meeting_id}/share", tags=["sharing"])
async def share_meeting(meeting_id: str, body: ShareRequest) -> dict[str, str]:
    """Share meeting notes to Slack and/or email."""
    try:
        airtable = AirtableClient()
        meeting_data = await airtable.get_meeting(meeting_id)
        if not meeting_data:
            raise HTTPException(status_code=404, detail="Meeting not found")

        # Reconstruct a lightweight MeetingRecord for the notifier
        summary = None
        if meeting_data.get("ExecutiveSummary"):
            summary = Summary(
                executive_summary=meeting_data.get("ExecutiveSummary", ""),
                key_decisions=(
                    meeting_data.get("KeyDecisions", "").split("\n")
                    if meeting_data.get("KeyDecisions")
                    else []
                ),
                discussion_topics=(
                    meeting_data.get("DiscussionTopics", "").split("\n")
                    if meeting_data.get("DiscussionTopics")
                    else []
                ),
                participants=(
                    [
                        p.strip()
                        for p in meeting_data.get("Participants", "").split(",")
                    ]
                    if meeting_data.get("Participants")
                    else []
                ),
            )

        action_records = await airtable.get_action_items(meeting_id)
        action_items = [
            ActionItem(
                description=r.get("Description", ""),
                assigned_to=r.get("AssignedTo"),
                deadline=r.get("Deadline"),
                priority=r.get("Priority", "medium"),
            )
            for r in action_records
        ]

        record = MeetingRecord(
            id=meeting_id,
            title=meeting_data.get("Title", "Untitled Meeting"),
            summary=summary,
            action_items=action_items if body.include_action_items else [],
        )

        notifier = NotifierService()

        if body.channel:
            await notifier.post_to_slack(record, channel=body.channel)

        if body.email_recipients:
            await notifier.send_email(record, recipients=body.email_recipients)

        return {"status": "shared", "meeting_id": meeting_id}

    except NotificationError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    except AirtableError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
