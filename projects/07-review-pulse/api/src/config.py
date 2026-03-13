"""Application configuration loaded from environment variables."""

from __future__ import annotations

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Central configuration for the ReviewPulse API."""

    # --- Application ---
    app_name: str = "ReviewPulse API"
    app_version: str = "1.0.0"
    debug: bool = False
    log_level: str = "INFO"
    allowed_origins: list[str] = ["*"]

    # --- OpenAI ---
    openai_api_key: str = Field(..., description="OpenAI API key")
    openai_model: str = Field(
        "gpt-4o",
        description="OpenAI model for sentiment analysis and response generation",
    )
    openai_embedding_model: str = "text-embedding-3-small"

    # --- Airtable ---
    airtable_api_key: str = Field(..., description="Airtable personal access token")
    airtable_base_id: str = Field(..., description="Airtable base ID")
    airtable_reviews_table: str = "Reviews"
    airtable_businesses_table: str = "Businesses"
    airtable_sentiment_table: str = "SentimentAnalysis"
    airtable_responses_table: str = "Responses"

    # --- Apify ---
    apify_api_token: str = Field("", description="Apify API token")
    apify_actor_id: str = Field(
        "", description="Apify actor ID for the review scraper"
    )

    # --- Alerts ---
    slack_webhook_url: str = Field("", description="Slack webhook for negative alerts")
    negative_threshold: float = Field(
        -0.3,
        description="Sentiment score threshold to trigger negative review alerts",
    )
    alert_min_rating: float = Field(
        2.0, description="Minimum star rating to trigger alerts"
    )

    # --- Rate Limiting ---
    rate_limit_per_minute: int = 60

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
    }


@lru_cache
def get_settings() -> Settings:
    """Return cached application settings."""
    return Settings()
