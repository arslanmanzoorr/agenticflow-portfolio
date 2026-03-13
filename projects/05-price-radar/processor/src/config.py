"""Application configuration loaded from environment variables.

Uses pydantic-settings so every value can be overridden with an env var
or a ``.env`` file placed next to the running process.
"""

from __future__ import annotations

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Central configuration for PriceRadar processor."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ---- Apify ----
    APIFY_API_TOKEN: str = Field(default="", description="Apify API token")
    APIFY_ACTOR_ID: str = Field(default="", description="Apify actor ID for the price scraper")

    # ---- OpenAI ----
    OPENAI_API_KEY: str = Field(default="", description="OpenAI API key for analysis summaries")

    # ---- Airtable ----
    AIRTABLE_API_KEY: str = Field(default="", description="Airtable personal access token")
    AIRTABLE_BASE_ID: str = Field(default="", description="Airtable base ID")
    AIRTABLE_PRODUCTS_TABLE: str = Field(default="Products", description="Products table name")
    AIRTABLE_HISTORY_TABLE: str = Field(default="PriceHistory", description="Price history table")
    AIRTABLE_COMPETITORS_TABLE: str = Field(default="Competitors", description="Competitors table")
    AIRTABLE_ALERTS_TABLE: str = Field(default="Alerts", description="Alerts table")

    # ---- Email / SMTP ----
    ALERT_EMAIL: str = Field(default="", description="Recipient email for price alerts")
    SMTP_HOST: str = Field(default="smtp.gmail.com", description="SMTP server hostname")
    SMTP_PORT: int = Field(default=587, description="SMTP server port")
    SMTP_USER: str = Field(default="", description="SMTP username")
    SMTP_PASSWORD: str = Field(default="", description="SMTP password or app password")

    # ---- Thresholds ----
    PRICE_CHANGE_THRESHOLD: float = Field(
        default=5.0,
        description="Minimum percentage change to trigger an alert",
    )

    # ---- Application ----
    APP_NAME: str = Field(default="PriceRadar")
    APP_VERSION: str = Field(default="1.0.0")
    DEBUG: bool = Field(default=False)


@lru_cache
def get_settings() -> Settings:
    """Return a cached Settings instance."""
    return Settings()


# Module-level alias for convenience (used by airtable_sync and other services).
settings = get_settings()
