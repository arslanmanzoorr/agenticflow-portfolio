"""Application configuration loaded from environment variables."""

from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Central configuration for FormBridge."""

    # --- Application ---
    app_name: str = "FormBridge"
    app_version: str = "1.0.0"
    debug: bool = False
    log_level: str = "INFO"

    # --- HubSpot ---
    hubspot_api_key: str = Field(default="", description="HubSpot private app access token")
    hubspot_portal_id: str = Field(default="", description="HubSpot portal/account ID")

    # --- Airtable ---
    airtable_api_key: str = Field(default="", description="Airtable personal access token")
    airtable_base_id: str = Field(default="", description="Airtable base ID")
    airtable_submissions_table: str = Field(
        default="Submissions", description="Table name for form submissions"
    )
    airtable_contacts_table: str = Field(
        default="Contacts", description="Table name for contacts"
    )

    # --- Slack ---
    slack_webhook_url: str = Field(default="", description="Slack incoming webhook URL")
    slack_channel: str = Field(default="#leads", description="Default Slack channel")
    slack_notify_on_error: bool = True
    slack_daily_digest: bool = True

    # --- Webhook Security ---
    webhook_secret: str = Field(default="", description="Shared secret for webhook verification")
    allowed_origins: list[str] = Field(default_factory=list, description="CORS allowed origins")

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
