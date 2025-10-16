"""Configuration for the application."""

# pylint: disable=too-few-public-methods

from __future__ import annotations

from functools import lru_cache

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()


class Config(BaseSettings):
    """Configuration for the application."""

    jira_project: str
    jira_epic_key: str
    jira_email: str
    jira_token: str
    jira_host: str
    jira_id: str | None = None

    @property
    def jira_url(self) -> str:
        """Return the Jira URL."""
        return f"https://{self.jira_host}/"

    class Config:
        """Pydantic configuration."""

        env_file = ".env"
        case_sensitive = False


@lru_cache
def get_settings() -> Config:
    """Return the settings."""
    return Config()
