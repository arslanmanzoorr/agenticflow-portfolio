"""Application configuration loaded from environment variables."""

from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings managed via environment variables."""

    # OpenAI
    openai_api_key: str = Field(..., description="OpenAI API key for Whisper and GPT")
    openai_model: str = Field(default="gpt-4o", description="GPT model for summarization")
    whisper_model: str = Field(default="whisper-1", description="Whisper model name")

    # Airtable
    airtable_api_key: str = Field(default="", description="Airtable personal access token")
    airtable_base_id: str = Field(default="", description="Airtable base ID")
    airtable_meetings_table: str = Field(
        default="Meetings", description="Airtable table for meetings"
    )
    airtable_actions_table: str = Field(
        default="ActionItems", description="Airtable table for action items"
    )

    # Slack
    slack_webhook_url: str = Field(default="", description="Slack incoming webhook URL")
    slack_default_channel: str = Field(
        default="#meeting-notes", description="Default Slack channel for notifications"
    )

    # Email (SMTP)
    smtp_host: str = Field(default="", description="SMTP server host")
    smtp_port: int = Field(default=587, description="SMTP server port")
    smtp_username: str = Field(default="", description="SMTP username")
    smtp_password: str = Field(default="", description="SMTP password")
    email_from: str = Field(
        default="meetingmind@example.com", description="Sender email address"
    )

    # Application
    upload_dir: str = Field(default="./uploads", description="Directory for audio uploads")
    max_file_size_mb: int = Field(default=100, description="Maximum upload file size in MB")
    app_env: str = Field(default="development", description="Application environment")
    log_level: str = Field(default="INFO", description="Logging level")
    port: int = Field(default=8000, description="Server port")

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}

    @property
    def upload_path(self) -> Path:
        """Return the upload directory as a Path, creating it if needed."""
        path = Path(self.upload_dir)
        path.mkdir(parents=True, exist_ok=True)
        return path


def get_settings() -> Settings:
    """Create and return application settings instance."""
    return Settings()
