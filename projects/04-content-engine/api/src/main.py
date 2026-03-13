"""ContentEngine API -- FastAPI application.

Provides endpoints for AI-powered social media content generation, scheduling,
and analytics backed by OpenAI and Airtable.
"""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from .config import get_settings
from .models.content import (
    AnalyticsResponse,
    BatchContentRequest,
    BatchContentResponse,
    ContentRecord,
    ContentRequest,
    ContentResponse,
    ContentStatus,
    Platform,
    PlatformAnalytics,
    ScheduleRequest,
    ScheduleResponse,
    Tone,
)
from .services.airtable_client import AirtableClient
from .services.content_generator import ContentGenerator
from .services.image_prompt import ImagePromptGenerator

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Application lifespan -- initialise shared service instances
# ---------------------------------------------------------------------------

_generator: ContentGenerator | None = None
_airtable: AirtableClient | None = None
_image_prompt: ImagePromptGenerator | None = None


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    """Initialise and tear down shared service singletons."""
    global _generator, _airtable, _image_prompt  # noqa: PLW0603

    settings = get_settings()
    _generator = ContentGenerator(settings)
    _airtable = AirtableClient(settings)
    _image_prompt = ImagePromptGenerator(settings)

    logger.info("ContentEngine API started (model=%s)", settings.openai_model)
    yield
    logger.info("ContentEngine API shutting down")


# ---------------------------------------------------------------------------
# FastAPI application
# ---------------------------------------------------------------------------

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="AI-powered social media content generation pipeline",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Dependency helpers
# ---------------------------------------------------------------------------


def _get_generator() -> ContentGenerator:
    if _generator is None:
        raise HTTPException(status_code=503, detail="Service not initialised")
    return _generator


def _get_airtable() -> AirtableClient:
    if _airtable is None:
        raise HTTPException(status_code=503, detail="Service not initialised")
    return _airtable


def _get_image_prompt() -> ImagePromptGenerator:
    if _image_prompt is None:
        raise HTTPException(status_code=503, detail="Service not initialised")
    return _image_prompt


# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------


@app.get("/health", tags=["system"])
async def health_check() -> dict[str, str]:
    """Return service health status."""
    return {"status": "ok", "service": "ContentEngine API"}


# ---------------------------------------------------------------------------
# POST /generate -- single-platform content generation
# ---------------------------------------------------------------------------


@app.post("/generate", response_model=ContentResponse, tags=["content"])
async def generate_content(request: ContentRequest) -> ContentResponse:
    """Generate social media content for a single platform.

    Uses OpenAI to create platform-optimised posts based on the provided topic,
    keywords, tone, and platform.  Optionally generates a companion DALL-E
    image prompt and persists the result to Airtable.
    """
    generator = _get_generator()
    airtable = _get_airtable()
    img_gen = _get_image_prompt()

    try:
        result = await generator.generate(request)

        # Generate a companion image prompt
        image_prompt = await img_gen.generate_prompt(
            result.content, request.platform
        )
        result.image_prompt = image_prompt

        # Persist to Airtable
        record = ContentRecord(
            id=result.id,
            topic=result.topic,
            platform=result.platform,
            tone=result.tone,
            content=result.content,
            hashtags=result.hashtags,
            image_prompt=result.image_prompt,
            character_count=result.character_count,
            status=result.status,
        )
        await airtable.create_content(record)

        return result

    except Exception as exc:
        logger.exception("Content generation failed")
        raise HTTPException(status_code=500, detail=str(exc)) from exc


# ---------------------------------------------------------------------------
# POST /batch -- multi-platform content generation
# ---------------------------------------------------------------------------


@app.post("/batch", response_model=BatchContentResponse, tags=["content"])
async def generate_batch_content(request: BatchContentRequest) -> BatchContentResponse:
    """Generate content for the same topic across multiple platforms.

    Creates one post per requested platform, each tailored to that platform's
    conventions and character limits.
    """
    generator = _get_generator()
    airtable = _get_airtable()
    img_gen = _get_image_prompt()

    results: list[ContentResponse] = []

    for platform in request.platforms:
        single_request = ContentRequest(
            topic=request.topic,
            keywords=request.keywords,
            platform=platform,
            tone=request.tone,
            include_hashtags=request.include_hashtags,
            include_emoji=request.include_emoji,
            language=request.language,
            additional_context=request.additional_context,
        )

        try:
            result = await generator.generate(single_request)
            result.image_prompt = await img_gen.generate_prompt(
                result.content, platform
            )

            record = ContentRecord(
                id=result.id,
                topic=result.topic,
                platform=result.platform,
                tone=result.tone,
                content=result.content,
                hashtags=result.hashtags,
                image_prompt=result.image_prompt,
                character_count=result.character_count,
                status=result.status,
            )
            await airtable.create_content(record)
            results.append(result)

        except Exception:
            logger.exception("Batch generation failed for platform=%s", platform.value)
            results.append(
                ContentResponse(
                    topic=request.topic,
                    platform=platform,
                    tone=request.tone,
                    content=f"[Generation failed for {platform.value}]",
                    character_count=0,
                    status=ContentStatus.FAILED,
                )
            )

    return BatchContentResponse(
        topic=request.topic,
        results=results,
        total_platforms=len(request.platforms),
    )


# ---------------------------------------------------------------------------
# GET /content/{id} -- retrieve generated content
# ---------------------------------------------------------------------------


@app.get("/content/{content_id}", response_model=ContentResponse, tags=["content"])
async def get_content(content_id: str) -> ContentResponse:
    """Retrieve a previously generated content piece by its ID."""
    airtable = _get_airtable()

    record = await airtable.get_content(content_id)
    if record is None:
        raise HTTPException(status_code=404, detail=f"Content '{content_id}' not found")

    return ContentResponse(
        id=record.id,
        topic=record.topic,
        platform=record.platform,
        tone=record.tone,
        content=record.content,
        hashtags=record.hashtags,
        image_prompt=record.image_prompt,
        character_count=record.character_count,
        created_at=record.created_at,
        status=record.status,
    )


# ---------------------------------------------------------------------------
# POST /schedule -- schedule content for publishing
# ---------------------------------------------------------------------------


@app.post("/schedule", response_model=ScheduleResponse, tags=["scheduling"])
async def schedule_content(request: ScheduleRequest) -> ScheduleResponse:
    """Schedule a content piece for future publishing.

    Marks the content record as *scheduled* and sets the target publish
    datetime.  The n8n publish-scheduler workflow picks up scheduled items
    whose publish time has arrived.
    """
    airtable = _get_airtable()

    record = await airtable.get_content(request.content_id)
    if record is None:
        raise HTTPException(
            status_code=404,
            detail=f"Content '{request.content_id}' not found",
        )

    if record.airtable_record_id is None:
        raise HTTPException(
            status_code=400,
            detail="Content record has no Airtable ID -- cannot update",
        )

    await airtable.update_content(
        record.airtable_record_id,
        {
            "Status": ContentStatus.SCHEDULED.value,
            "PublishAt": request.publish_at.isoformat(),
            "Platform": request.platform.value,
        },
    )

    return ScheduleResponse(
        content_id=request.content_id,
        platform=request.platform,
        publish_at=request.publish_at,
        status=ContentStatus.SCHEDULED,
    )


# ---------------------------------------------------------------------------
# GET /analytics -- content performance stats
# ---------------------------------------------------------------------------


@app.get("/analytics", response_model=AnalyticsResponse, tags=["analytics"])
async def get_analytics(
    platform: Platform | None = Query(default=None, description="Filter by platform"),
) -> AnalyticsResponse:
    """Retrieve aggregate content performance statistics.

    Summarises all generated content by status, platform, and recency.
    """
    airtable = _get_airtable()

    try:
        raw = await airtable.get_analytics()

        platform_analytics = [
            PlatformAnalytics(
                platform=Platform(pa["platform"]),
                total_posts=pa["total_posts"],
                published=pa["published"],
                scheduled=pa["scheduled"],
                drafts=pa["drafts"],
                avg_character_count=pa["avg_character_count"],
            )
            for pa in raw.get("by_platform", [])
            if platform is None or pa["platform"] == platform.value
        ]

        return AnalyticsResponse(
            total_content=raw["total_content"],
            by_platform=platform_analytics,
            by_status=raw["by_status"],
            generated_today=raw["generated_today"],
            generated_this_week=raw["generated_this_week"],
        )

    except Exception as exc:
        logger.exception("Analytics retrieval failed")
        raise HTTPException(status_code=500, detail=str(exc)) from exc
