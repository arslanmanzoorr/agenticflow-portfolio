"""Pydantic models for the ContentEngine API."""

from __future__ import annotations

import uuid
from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class Platform(str, Enum):
    """Supported social media platforms."""

    LINKEDIN = "linkedin"
    TWITTER = "twitter"
    INSTAGRAM = "instagram"
    FACEBOOK = "facebook"
    THREADS = "threads"


class Tone(str, Enum):
    """Content tone presets."""

    PROFESSIONAL = "professional"
    CASUAL = "casual"
    HUMOROUS = "humorous"
    INSPIRATIONAL = "inspirational"
    EDUCATIONAL = "educational"
    PERSUASIVE = "persuasive"


class ContentStatus(str, Enum):
    """Lifecycle status of a content piece."""

    DRAFT = "draft"
    REVIEW = "review"
    APPROVED = "approved"
    SCHEDULED = "scheduled"
    PUBLISHED = "published"
    FAILED = "failed"


# ---------------------------------------------------------------------------
# Request models
# ---------------------------------------------------------------------------


class ContentRequest(BaseModel):
    """Payload for generating content on a single platform."""

    topic: str = Field(..., min_length=3, max_length=500, description="Content topic or headline")
    keywords: list[str] = Field(default_factory=list, max_length=10, description="SEO / relevance keywords")
    platform: Platform = Field(..., description="Target social media platform")
    tone: Tone = Field(default=Tone.PROFESSIONAL, description="Desired content tone")
    max_length: Optional[int] = Field(
        default=None,
        gt=0,
        le=5000,
        description="Maximum character count (platform defaults apply when omitted)",
    )
    include_hashtags: bool = Field(default=True, description="Whether to append relevant hashtags")
    include_emoji: bool = Field(default=True, description="Whether to include emoji")
    language: str = Field(default="en", max_length=5, description="ISO 639-1 language code")
    additional_context: Optional[str] = Field(
        default=None, max_length=2000, description="Extra context or brand guidelines"
    )


class BatchContentRequest(BaseModel):
    """Generate content for the same topic across multiple platforms."""

    topic: str = Field(..., min_length=3, max_length=500)
    keywords: list[str] = Field(default_factory=list, max_length=10)
    platforms: list[Platform] = Field(..., min_length=1, max_length=5)
    tone: Tone = Field(default=Tone.PROFESSIONAL)
    include_hashtags: bool = Field(default=True)
    include_emoji: bool = Field(default=True)
    language: str = Field(default="en", max_length=5)
    additional_context: Optional[str] = Field(default=None, max_length=2000)


class ScheduleRequest(BaseModel):
    """Schedule a piece of generated content for publishing."""

    content_id: str = Field(..., description="ID of the generated content record")
    publish_at: datetime = Field(..., description="UTC datetime to publish")
    platform: Platform = Field(..., description="Target platform")
    auto_publish: bool = Field(default=False, description="If true, publish automatically via webhook")


# ---------------------------------------------------------------------------
# Response models
# ---------------------------------------------------------------------------


class ContentResponse(BaseModel):
    """Single generated content piece."""

    id: str = Field(default_factory=lambda: uuid.uuid4().hex[:12])
    topic: str
    platform: Platform
    tone: Tone
    content: str = Field(..., description="The generated post / caption text")
    hashtags: list[str] = Field(default_factory=list)
    image_prompt: Optional[str] = Field(default=None, description="DALL-E image prompt suggestion")
    character_count: int = Field(..., ge=0)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    status: ContentStatus = Field(default=ContentStatus.DRAFT)


class BatchContentResponse(BaseModel):
    """Results of a multi-platform batch generation."""

    topic: str
    results: list[ContentResponse]
    total_platforms: int
    created_at: datetime = Field(default_factory=datetime.utcnow)


class ScheduleResponse(BaseModel):
    """Confirmation that content has been scheduled."""

    content_id: str
    platform: Platform
    publish_at: datetime
    status: ContentStatus = Field(default=ContentStatus.SCHEDULED)
    message: str = "Content scheduled successfully"


class PlatformAnalytics(BaseModel):
    """Per-platform aggregate analytics."""

    platform: Platform
    total_posts: int = 0
    published: int = 0
    scheduled: int = 0
    drafts: int = 0
    avg_character_count: float = 0.0


class AnalyticsResponse(BaseModel):
    """Content performance summary."""

    total_content: int = 0
    by_platform: list[PlatformAnalytics] = Field(default_factory=list)
    by_status: dict[str, int] = Field(default_factory=dict)
    generated_today: int = 0
    generated_this_week: int = 0


class ContentRecord(BaseModel):
    """Full content record stored in Airtable."""

    id: str = Field(default_factory=lambda: uuid.uuid4().hex[:12])
    topic: str
    platform: Platform
    tone: Tone
    content: str
    hashtags: list[str] = Field(default_factory=list)
    image_prompt: Optional[str] = None
    character_count: int = 0
    status: ContentStatus = Field(default=ContentStatus.DRAFT)
    publish_at: Optional[datetime] = None
    published_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    airtable_record_id: Optional[str] = None
