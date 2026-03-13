"""Pydantic models for meeting domain objects."""

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class Priority(str, Enum):
    """Priority levels for action items."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class TranscriptSegment(BaseModel):
    """A single timestamped segment of a transcript."""

    start: float = Field(..., description="Start time in seconds")
    end: float = Field(..., description="End time in seconds")
    text: str = Field(..., description="Transcribed text for this segment")
    speaker: Optional[str] = Field(default=None, description="Identified speaker name")


class Transcript(BaseModel):
    """Full meeting transcript with segments and metadata."""

    full_text: str = Field(..., description="Complete transcript as plain text")
    segments: list[TranscriptSegment] = Field(
        default_factory=list, description="Timestamped segments"
    )
    language: str = Field(default="en", description="Detected language code")
    duration_seconds: float = Field(default=0.0, description="Total audio duration")


class ActionItem(BaseModel):
    """An extracted action item from a meeting."""

    description: str = Field(..., description="What needs to be done")
    assigned_to: Optional[str] = Field(
        default=None, description="Person responsible for this action"
    )
    deadline: Optional[str] = Field(
        default=None, description="Due date or timeframe for completion"
    )
    priority: Priority = Field(default=Priority.MEDIUM, description="Priority level")


class Summary(BaseModel):
    """GPT-generated meeting summary."""

    executive_summary: str = Field(..., description="Brief executive summary")
    key_decisions: list[str] = Field(
        default_factory=list, description="Key decisions made during the meeting"
    )
    discussion_topics: list[str] = Field(
        default_factory=list, description="Main topics discussed"
    )
    participants: list[str] = Field(
        default_factory=list, description="Identified meeting participants"
    )
    meeting_date: Optional[str] = Field(
        default=None, description="Date of the meeting"
    )
    duration_minutes: Optional[float] = Field(
        default=None, description="Meeting duration in minutes"
    )


class MeetingRecord(BaseModel):
    """Complete meeting record combining all processed data."""

    id: str = Field(..., description="Unique meeting identifier")
    title: str = Field(default="Untitled Meeting", description="Meeting title")
    created_at: datetime = Field(
        default_factory=datetime.utcnow, description="Record creation timestamp"
    )
    audio_filename: Optional[str] = Field(
        default=None, description="Original audio file name"
    )
    transcript: Optional[Transcript] = Field(
        default=None, description="Transcription result"
    )
    summary: Optional[Summary] = Field(
        default=None, description="GPT-generated summary"
    )
    action_items: list[ActionItem] = Field(
        default_factory=list, description="Extracted action items"
    )
    status: str = Field(default="pending", description="Processing status")


class ShareRequest(BaseModel):
    """Request to share meeting notes via Slack or email."""

    channel: Optional[str] = Field(
        default=None, description="Slack channel to post to (e.g. #team-standup)"
    )
    email_recipients: list[str] = Field(
        default_factory=list, description="Email addresses to send recap to"
    )
    include_transcript: bool = Field(
        default=False, description="Whether to include the full transcript"
    )
    include_action_items: bool = Field(
        default=True, description="Whether to include action items"
    )


class TranscribeResponse(BaseModel):
    """Response from the transcription endpoint."""

    meeting_id: str
    transcript: Transcript


class SummarizeRequest(BaseModel):
    """Request body for the summarize endpoint."""

    transcript_text: str = Field(..., description="Transcript text to summarize")
    meeting_id: Optional[str] = Field(
        default=None, description="Meeting ID to attach summary to"
    )


class ActionItemsRequest(BaseModel):
    """Request body for the action items endpoint."""

    transcript_text: str = Field(
        ..., description="Transcript text to extract actions from"
    )
    meeting_id: Optional[str] = Field(
        default=None, description="Meeting ID to attach actions to"
    )
