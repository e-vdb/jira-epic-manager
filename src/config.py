"""Configuration for the application."""

# pylint: disable=too-few-public-methods

from __future__ import annotations

from functools import lru_cache

from dotenv import load_dotenv
from pydantic import model_validator
from pydantic_settings import BaseSettings

from src.exceptions import JiraEpicProjectMismatchError

load_dotenv()


class Config(BaseSettings):
    """Configuration for the application."""

    jira_project: str
    jira_epic_key: str
    jira_email: str
    jira_token: str
    jira_host: str
    jira_id: str

    @property
    def jira_url(self) -> str:
        """Return the Jira URL."""
        return f"https://{self.jira_host}/"

    @model_validator(mode="after")
    def validate_project_and_epic_key(self) -> None:
        """Validate that the epic key matches the project key."""
        epic_key_prefix = self.jira_epic_key.split("-")[0]
        if epic_key_prefix != self.jira_project:
            raise JiraEpicProjectMismatchError(
                epic_key=self.jira_epic_key,
                project_key=self.jira_project,
            )

    class Config:
        """Pydantic configuration."""

        env_file = ".env"
        case_sensitive = False


@lru_cache
def get_settings() -> Config:
    """Return the settings."""
    return Config()
