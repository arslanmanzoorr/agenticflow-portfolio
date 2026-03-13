"""ReviewPulse - Review Aggregation & Sentiment Analysis API."""

from __future__ import annotations

import logging
import time
import uuid
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Any, AsyncIterator

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from openai import AsyncOpenAI

from api.src.config import Settings, get_settings
from api.src.models.review import (
    AnalyzeRequest,
    AnalyzeResponse,
    DashboardData,
    Review,
    ReviewWebhookPayload,
    SentimentResult,
)
from api.src.services.airtable_client import AirtableClient, AirtableError
from api.src.services.alert_service import AlertService
from api.src.services.sentiment import SentimentAnalyzer

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Application state shared across requests
# ---------------------------------------------------------------------------
_state: dict[str, Any] = {}


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Startup / shutdown lifecycle hook."""
    settings = get_settings()
    _state["settings"] = settings
    _state["analyzer"] = SentimentAnalyzer(settings)
    _state["airtable"] = AirtableClient(settings)
    _state["alerts"] = AlertService(settings)
    logger.info("ReviewPulse API v%s starting up", settings.app_version)
    yield
    logger.info("ReviewPulse API shutting down")


app = FastAPI(
    title="ReviewPulse API",
    description=(
        "Aggregates customer reviews from multiple platforms, runs AI-powered "
        "sentiment analysis, persists data to Airtable, and dispatches Slack "
        "alerts for negative reviews."
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
# Helpers
# ---------------------------------------------------------------------------

def _settings() -> Settings:
    return _state["settings"]


def _analyzer() -> SentimentAnalyzer:
    return _state["analyzer"]


def _airtable() -> AirtableClient:
    return _state["airtable"]


def _alert_svc() -> AlertService:
    return _state["alerts"]


# ---------------------------------------------------------------------------
# Health
# ---------------------------------------------------------------------------

@app.get("/health", tags=["health"])
async def health() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "healthy", "service": "review-pulse", "version": "1.0.0"}


# ---------------------------------------------------------------------------
# Webhook - receive scraped reviews
# ---------------------------------------------------------------------------

@app.post("/webhook/reviews", tags=["webhook"])
async def receive_reviews(payload: ReviewWebhookPayload) -> dict[str, Any]:
    """Receive scraped reviews from Apify / n8n.

    Persists each review to Airtable and returns the count of saved reviews.
    """
    airtable = _airtable()
    saved = 0

    for review in payload.reviews:
        try:
            review_data = review.model_dump()
            review_data["business_id"] = payload.business_id
            review_data["platform"] = review.platform.value
            airtable.save_review(review_data)
            saved += 1
        except AirtableError:
            logger.warning("Failed to save review %s", review.review_id)

    return {
        "status": "accepted",
        "received": len(payload.reviews),
        "saved": saved,
        "business_id": payload.business_id,
    }


# ---------------------------------------------------------------------------
# Analyze - sentiment analysis
# ---------------------------------------------------------------------------

@app.post("/analyze", response_model=AnalyzeResponse, tags=["analysis"])
async def analyze_reviews(request: AnalyzeRequest) -> AnalyzeResponse:
    """Run sentiment analysis on a batch of reviews.

    Each result is persisted to Airtable and checked against the alert
    threshold. Negative reviews trigger a Slack notification.
    """
    analyzer = _analyzer()
    airtable = _airtable()
    alert_svc = _alert_svc()

    response = await analyzer.analyze_batch(request)

    # Persist results and check alerts
    for result, review in zip(response.results, request.reviews):
        try:
            airtable.save_summary(result.model_dump())
        except AirtableError:
            logger.warning("Failed to persist sentiment for %s", result.review_id)

        try:
            await alert_svc.check_alerts(review, result)
        except Exception:
            logger.warning("Alert check failed for %s", result.review_id)

    return response


# ---------------------------------------------------------------------------
# Reviews CRUD
# ---------------------------------------------------------------------------

@app.get("/reviews", tags=["reviews"])
async def list_reviews(
    source: str | None = Query(None, description="Filter by platform (e.g. google_maps)"),
    rating: float | None = Query(None, ge=0, le=5, description="Filter by exact rating"),
    sentiment: str | None = Query(None, description="Filter by sentiment label"),
    limit: int = Query(100, ge=1, le=500),
) -> list[dict[str, Any]]:
    """List reviews with optional filters."""
    filters: dict[str, str] = {}
    if source:
        filters["Platform"] = source
    if rating is not None:
        filters["Rating"] = str(rating)
    if sentiment:
        filters["Label"] = sentiment

    try:
        return _airtable().get_reviews(filters=filters if filters else None, max_records=limit)
    except AirtableError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@app.get("/reviews/{review_id}", tags=["reviews"])
async def get_review(review_id: str) -> dict[str, Any]:
    """Get a single review by its ReviewID."""
    try:
        results = _airtable().get_reviews(filters={"ReviewID": review_id}, max_records=1)
        if not results:
            raise HTTPException(status_code=404, detail="Review not found")
        return results[0]
    except AirtableError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


# ---------------------------------------------------------------------------
# Dashboard
# ---------------------------------------------------------------------------

@app.get("/dashboard", response_model=DashboardData, tags=["dashboard"])
async def dashboard() -> DashboardData:
    """Return aggregate stats: avg rating, sentiment breakdown, count by source."""
    try:
        stats = _airtable().get_review_stats()
        recent = _airtable().get_reviews(max_records=10)
        alerts_resp = _alert_svc().get_recent_alerts(hours=168)

        recent_reviews = []
        for r in recent:
            try:
                recent_reviews.append(
                    Review(
                        review_id=r.get("ReviewID", ""),
                        platform=r.get("Platform", "manual"),
                        rating=r.get("Rating", 0),
                        text=r.get("Text", ""),
                        date=r.get("Date", ""),
                    )
                )
            except Exception:
                continue

        return DashboardData(
            business_id="all",
            total_reviews=stats["total_reviews"],
            average_rating=stats["average_rating"],
            average_sentiment=0.0,
            sentiment_distribution=stats["sentiment_breakdown"],
            platform_stats=[],
            category_breakdown=[],
            recent_reviews=recent_reviews,
            recent_alerts=[
                a.model_dump() for a in alerts_resp.alerts[:5]
            ],
        )
    except AirtableError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


# ---------------------------------------------------------------------------
# Summarize - AI weekly/monthly summaries
# ---------------------------------------------------------------------------

@app.post("/summarize", tags=["summaries"])
async def summarize_reviews(
    period_days: int = Query(7, ge=1, le=90, description="Number of days to look back"),
) -> dict[str, Any]:
    """Generate an AI-powered summary of recent reviews using OpenAI.

    Fetches recent reviews from Airtable and asks GPT to produce a structured
    summary covering trends, strengths, weaknesses, and recommendations.
    """
    settings = _settings()
    airtable = _airtable()

    try:
        reviews = airtable.get_reviews(max_records=200)
    except AirtableError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    if not reviews:
        return {"summary": "No reviews found for the requested period.", "review_count": 0}

    review_texts = []
    for r in reviews[:100]:
        text = r.get("Text", "")
        rating = r.get("Rating", "N/A")
        platform = r.get("Platform", "unknown")
        if text:
            review_texts.append(f"[{platform} - {rating}/5] {text}")

    prompt = (
        f"You are a business analyst. Summarize the following {len(review_texts)} customer "
        f"reviews from the last {period_days} days. Provide:\n"
        "1. Executive summary (2-3 sentences)\n"
        "2. Top strengths mentioned by customers\n"
        "3. Top weaknesses or complaints\n"
        "4. Sentiment trend overview\n"
        "5. Actionable recommendations\n\n"
        "Reviews:\n" + "\n---\n".join(review_texts)
    )

    try:
        client = AsyncOpenAI(api_key=settings.openai_api_key)
        response = await client.chat.completions.create(
            model=settings.openai_model,
            messages=[
                {"role": "system", "content": "You are a business review analyst."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.4,
            max_tokens=1500,
        )

        summary_text = response.choices[0].message.content or ""
        summary_record = {
            "review_id": f"summary-{uuid.uuid4().hex[:8]}",
            "overall_score": 0.0,
            "label": "neutral",
            "confidence": 1.0,
            "key_phrases": [],
            "summary": summary_text,
            "model_used": settings.openai_model,
            "analyzed_at": datetime.utcnow().isoformat(),
        }

        try:
            airtable.save_summary(summary_record)
        except AirtableError:
            logger.warning("Failed to persist summary to Airtable")

        return {
            "summary": summary_text,
            "review_count": len(review_texts),
            "period_days": period_days,
            "generated_at": datetime.utcnow().isoformat(),
        }

    except Exception as exc:
        logger.error("Summary generation failed: %s", exc, exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to generate summary") from exc


@app.get("/summaries", tags=["summaries"])
async def list_summaries(
    limit: int = Query(20, ge=1, le=100),
) -> list[dict[str, Any]]:
    """List previously generated review summaries."""
    try:
        return _airtable().list_summaries(max_records=limit)
    except AirtableError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
