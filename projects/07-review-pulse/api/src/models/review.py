"""Pydantic models for reviews, sentiment, trends, and dashboard data."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class Platform(str, Enum):
    GOOGLE_MAPS = "google_maps"
    YELP = "yelp"
    TRUSTPILOT = "trustpilot"
    MANUAL = "manual"


class SentimentLabel(str, Enum):
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"


class ReviewCategory(str, Enum):
    SERVICE = "service"
    QUALITY = "quality"
    PRICE = "price"
    AMBIANCE = "ambiance"
    CLEANLINESS = "cleanliness"
    SPEED = "speed"
    COMMUNICATION = "communication"
    VALUE = "value"


class ResponseTone(str, Enum):
    PROFESSIONAL = "professional"
    FRIENDLY = "friendly"
    EMPATHETIC = "empathetic"
    APOLOGETIC = "apologetic"


# ---------------------------------------------------------------------------
# Core review model
# ---------------------------------------------------------------------------

class Review(BaseModel):
    """A single review from any platform."""

    review_id: str = Field(..., description="Unique review identifier")
    platform: Platform
    business_id: str = Field("", description="Internal business identifier")
    business_name: str = ""
    business_url: str = ""
    reviewer_name: str = "Anonymous"
    rating: float = Field(..., ge=0, le=5, description="Normalised 0-5 rating")
    max_rating: float = 5.0
    text: str = ""
    date: str = Field(..., description="Review date in YYYY-MM-DD format")
    scraped_at: str = Field(
        default_factory=lambda: datetime.utcnow().isoformat(),
        description="ISO-8601 timestamp of when the review was scraped",
    )
    language: str = "en"
    metadata: dict[str, Any] = Field(default_factory=dict)


class ReviewWebhookPayload(BaseModel):
    """Payload received from the Apify scraper webhook."""

    business_id: str
    reviews: list[Review]
    total_count: int = 0
    scraped_at: str = ""


# ---------------------------------------------------------------------------
# Sentiment analysis
# ---------------------------------------------------------------------------

class CategoryScore(BaseModel):
    """Sentiment score for a specific review category."""

    category: ReviewCategory
    score: float = Field(..., ge=-1, le=1)
    confidence: float = Field(0.0, ge=0, le=1)
    mentions: list[str] = Field(
        default_factory=list, description="Key phrases that mention this category"
    )


class SentimentResult(BaseModel):
    """Full sentiment analysis result for a single review."""

    review_id: str
    overall_score: float = Field(
        ..., ge=-1, le=1, description="Overall sentiment score (-1 to 1)"
    )
    label: SentimentLabel
    confidence: float = Field(..., ge=0, le=1)
    categories: list[CategoryScore] = Field(default_factory=list)
    key_phrases: list[str] = Field(
        default_factory=list, description="Important phrases extracted from the review"
    )
    summary: str = Field("", description="One-sentence AI summary of the review")
    language: str = "en"
    model_used: str = ""
    analyzed_at: str = Field(
        default_factory=lambda: datetime.utcnow().isoformat()
    )


class AnalyzeRequest(BaseModel):
    """Request to analyze one or more reviews."""

    reviews: list[Review]
    include_categories: bool = True
    include_key_phrases: bool = True
    include_summary: bool = True


class AnalyzeResponse(BaseModel):
    """Response containing sentiment analysis results."""

    results: list[SentimentResult]
    processing_time_ms: float = 0
    total_analyzed: int = 0


# ---------------------------------------------------------------------------
# Response suggestions
# ---------------------------------------------------------------------------

class ResponseSuggestion(BaseModel):
    """AI-generated response suggestion for a review."""

    review_id: str
    tone: ResponseTone
    response_text: str
    key_points_addressed: list[str] = Field(default_factory=list)
    generated_at: str = Field(
        default_factory=lambda: datetime.utcnow().isoformat()
    )


class RespondRequest(BaseModel):
    """Request to generate a response for a review."""

    review: Review
    sentiment: SentimentResult | None = None
    tone: ResponseTone = ResponseTone.PROFESSIONAL
    business_context: str = Field(
        "",
        description="Additional context about the business for personalised responses",
    )
    max_length: int = Field(300, ge=50, le=1000)


# ---------------------------------------------------------------------------
# Trends & dashboard
# ---------------------------------------------------------------------------

class TrendPoint(BaseModel):
    """A single data point in a time-series trend."""

    date: str
    average_score: float
    review_count: int
    positive_count: int = 0
    neutral_count: int = 0
    negative_count: int = 0


class CategoryBreakdown(BaseModel):
    """Aggregated sentiment breakdown by category."""

    category: ReviewCategory
    average_score: float
    mention_count: int
    trend: str = Field(
        "stable", description="Trend direction: improving, declining, stable"
    )


class PlatformStats(BaseModel):
    """Per-platform statistics."""

    platform: Platform
    review_count: int
    average_rating: float
    average_sentiment: float
    latest_review_date: str = ""


class TrendData(BaseModel):
    """Trend analysis data for a business."""

    business_id: str
    period_start: str
    period_end: str
    interval: str = Field("week", description="Aggregation interval: day, week, month")
    data_points: list[TrendPoint] = Field(default_factory=list)
    category_breakdown: list[CategoryBreakdown] = Field(default_factory=list)
    platform_stats: list[PlatformStats] = Field(default_factory=list)
    overall_trend: str = "stable"
    total_reviews: int = 0


class DashboardData(BaseModel):
    """Aggregated dashboard data for a business."""

    business_id: str
    business_name: str = ""
    total_reviews: int = 0
    average_rating: float = 0.0
    average_sentiment: float = 0.0
    sentiment_distribution: dict[str, int] = Field(
        default_factory=lambda: {"positive": 0, "neutral": 0, "negative": 0}
    )
    rating_distribution: dict[str, int] = Field(
        default_factory=lambda: {"1": 0, "2": 0, "3": 0, "4": 0, "5": 0}
    )
    platform_stats: list[PlatformStats] = Field(default_factory=list)
    category_breakdown: list[CategoryBreakdown] = Field(default_factory=list)
    recent_reviews: list[Review] = Field(default_factory=list)
    recent_alerts: list[dict[str, Any]] = Field(default_factory=list)
    trends: TrendData | None = None
    generated_at: str = Field(
        default_factory=lambda: datetime.utcnow().isoformat()
    )


# ---------------------------------------------------------------------------
# Alerts
# ---------------------------------------------------------------------------

class AlertItem(BaseModel):
    """A negative review alert."""

    alert_id: str
    review: Review
    sentiment: SentimentResult
    reason: str
    severity: str = Field("medium", description="low, medium, high, critical")
    acknowledged: bool = False
    created_at: str = Field(
        default_factory=lambda: datetime.utcnow().isoformat()
    )


class AlertsResponse(BaseModel):
    """Response containing alerts."""

    alerts: list[AlertItem]
    total_count: int = 0
    unacknowledged_count: int = 0
