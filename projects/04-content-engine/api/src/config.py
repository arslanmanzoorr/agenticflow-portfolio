"""Application configuration via environment variables.

Uses *pydantic-settings* so every value can be overridden with an env var or
a ``.env`` file placed next to the running process.
"""

from __future__ import annotations

from functools import lru_cache
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Central configuration for the ContentEngine API."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ---- OpenAI ----
    openai_api_key: str = Field(..., description="OpenAI API key")
    openai_model: str = Field(default="gpt-4o", description="Chat completion model")
    openai_max_tokens: int = Field(default=1024, ge=64, le=4096)
    openai_temperature: float = Field(default=0.7, ge=0.0, le=2.0)

    # ---- Airtable ----
    airtable_api_key: str = Field(..., description="Airtable personal access token")
    airtable_base_id: str = Field(..., description="Airtable base ID (appXXXXXXXXXXXXXX)")
    airtable_content_table: str = Field(
        default="Generated Content",
        description="Table name for generated content records",
    )
    airtable_calendar_table: str = Field(
        default="Content Calendar",
        description="Table name for the editorial calendar",
    )

    # ---- API settings ----
    app_name: str = Field(default="ContentEngine API")
    app_version: str = Field(default="1.0.0")
    debug: bool = Field(default=False)
    cors_origins: list[str] = Field(default=["*"])

    # ---- Optional integrations ----
    slack_webhook_url: Optional[str] = Field(default=None, description="Slack incoming-webhook URL")
    n8n_webhook_url: Optional[str] = Field(default=None, description="n8n webhook trigger URL")


@lru_cache
def get_settings() -> Settings:
    """Return a cached ``Settings`` instance.

    The cache ensures environment variables and the ``.env`` file are read only
    once per process lifetime.
    """
    return Settings()  # type: ignore[call-arg]
