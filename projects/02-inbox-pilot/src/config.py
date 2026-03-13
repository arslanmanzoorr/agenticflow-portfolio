"""Application configuration loaded from environment variables."""

from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings managed via environment variables."""

    openai_api_key: str = Field(..., description="OpenAI API key")
    gmail_credentials_path: str = Field(
        default="./credentials/gmail_credentials.json",
        description="Path to Gmail OAuth2 credentials",
    )
    airtable_api_key: str = Field(default="", description="Airtable API key")
    airtable_base_id: str = Field(default="", description="Airtable base ID")
    app_env: str = Field(default="development", description="Application environment")
    log_level: str = Field(default="INFO", description="Logging level")
    port: int = Field(default=8000, description="Server port")

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


def get_settings() -> Settings:
    """Create and return application settings instance."""
    return Settings()
