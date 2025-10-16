"""Custom exceptions for the application."""

from __future__ import annotations


class JiraError(Exception):
    """Base exception for all Jira-related errors."""

    def __init__(self, message: str, details: dict | None = None) -> None:
        """Initialize the exception.

        Parameters
        ----------
        message : str
            Error message.
        details : dict | None
            Additional error details (e.g., response data, issue keys).

        """
        super().__init__(message)
        self.message = message
        self.details = details or {}


class JiraProjectNotFoundError(JiraError):
    """Raised when the specified Jira project doesn't exist."""

    def __init__(self, project_key: str) -> None:
        """Initialize the exception."""
        message = f"Jira project not found: {project_key}"
        super().__init__(message, {"project_key": project_key})
        self.project_key = project_key


class JiraEpicNotFoundError(JiraError):
    """Raised when the specified epic doesn't exist."""

    def __init__(self, epic_key: str) -> None:
        """Initialize the exception."""
        message = f"Jira epic not found: {epic_key}"
        super().__init__(message, {"epic_key": epic_key})
        self.epic_key = epic_key


class JiraEpicProjectMismatchError(JiraError):
    """Raised when the epic key doesn't match the project key."""

    def __init__(self, epic_key: str, project_key: str) -> None:
        """Initialize the exception."""
        message = f"Jira epic {epic_key} doesn't match project {project_key}"
        super().__init__(message, {"epic_key": epic_key, "project_key": project_key})
        self.epic_key = epic_key
        self.project_key = project_key


class StoryCreationError(JiraError):
    """Raised when story creation fails."""

    def __init__(
        self,
        story_summary: str,
        original_error: Exception | None = None,
    ) -> None:
        """Initialize the exception."""
        message = f"Failed to create story: {story_summary}"
        details = {"story_summary": story_summary}
        if original_error:
            details["original_error"] = str(original_error)
            message = f"{message} - {original_error!s}"
        super().__init__(message, details)
        self.story_summary = story_summary
        self.original_error = original_error
