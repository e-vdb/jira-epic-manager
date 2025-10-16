"""Module to create Jira stories within an epic."""

# pylint: disable=too-many-positional-arguments, logging-too-many-args
from __future__ import annotations

from typing import TYPE_CHECKING

from atlassian import Jira
from requests import HTTPError

from src.config import get_settings
from src.exceptions import JiraEpicNotFoundError, StoryCreationError
from src.logging_config import setup_logger

logger = setup_logger(name="jira_epic")

if TYPE_CHECKING:
    from src.schema import Story, Task


class JiraEpic:
    """Class to create Jira issues within an epic."""

    def __init__(self) -> None:
        """Set up the Jira client."""
        self.config = get_settings()
        self.jira = self.set_up_client()
        self._verify_epic_exists()

    def set_up_client(self) -> Jira:
        """Set up Jira client."""
        return Jira(
            url=self.config.jira_url,
            username=self.config.jira_email,
            password=self.config.jira_token,
        )

    def _verify_epic_exists(self) -> None:
        """Verify that the configured epic exists.

        Raises
        ------
        JiraEpicNotFoundError
            If the epic doesn't exist.

        """
        try:
            self.jira.issue(self.config.jira_epic_key)
            logger.info("Verified epic %s exists", self.config.jira_epic_key)
        except Exception as e:
            raise JiraEpicNotFoundError(self.config.jira_epic_key) from e

    def _get_assignee_id(self, assignee_id: str | None) -> str:
        """Get assignee ID, falling back to default from config.

        Parameters
        ----------
        assignee_id : str | None
            The assignee ID from the story/task, or None.

        Returns
        -------
        str
            The assignee ID to use.

        """
        return assignee_id or self.config.jira_id

    def _build_issue_fields(  # pylint: disable=too-many-arguments
        self,
        summary: str,
        description: str,
        issue_type: str,
        parent_key: str,
        assignee_id: str | None = None,
    ) -> dict:
        """Build common issue fields dictionary.

        Parameters
        ----------
        summary : str
            Issue summary.
        description : str
            Issue description.
        issue_type : str
            Issue type (Story, Sub-task, etc.).
        parent_key : str
            Parent issue key.
        assignee_id : str | None
            Assignee ID, optional.

        Returns
        -------
        dict
            Issue fields dictionary.

        """
        return {
            "project": {"key": self.config.jira_project},
            "summary": summary,
            "description": description,
            "issuetype": {"name": issue_type},
            "parent": {"key": parent_key},
            "assignee": {"id": self._get_assignee_id(assignee_id)},
        }

    def create_story_within_epic(self, story: Story) -> str:
        """Create a story for a market and return the issue key.

        Parameters
        ----------
        story : Story
            Story to be created.

        Returns
        -------
        str | None
            The issue key of the created story
            or None if the story could not be created.

        """
        fields = self._build_issue_fields(
            summary=story.summary,
            description=story.description,
            issue_type="Story",
            parent_key=self.config.jira_epic_key,
            assignee_id=story.assignee_id,
        )
        try:
            response = self.jira.create_issue(fields=fields)
            logger.info(
                "Created story '%s' with key %s",
                story.summary,
                response["key"],
            )
            return response["key"]
        except HTTPError as e:
            logger.exception("Failed to create story %s", story.summary)
            raise StoryCreationError(
                story_summary=story.summary,
                original_error=e,
            ) from e
        except Exception as e:  # pylint: disable=broad-exception-caught
            logger.exception(
                "Unexpected error creating story %s",
                story.summary,
            )
            raise StoryCreationError(
                story_summary=story.summary,
            ) from e

    def create_sub_tasks_in_story(
        self,
        all_tasks: list[Task],
        parent_key: str,
    ) -> None:
        """Create sub-tasks from a dictionary into a story.

        Parameters
        ----------
        all_tasks : list[Task]
            List of tasks to be created.
        parent_key : str
            The issue key of the story.

        Returns
        -------
        None

        """
        failed_tasks = []
        for task in all_tasks:
            fields = self._build_issue_fields(
                summary=task.summary,
                description=task.description,
                issue_type="Sub-task",
                parent_key=parent_key,
                assignee_id=task.assignee_id,
            )
            try:
                response = self.jira.create_issue(fields=fields)
                logger.info(
                    "Created sub-task '%s' with key %s under %s",
                    task.summary,
                    response["key"],
                    parent_key,
                )
            except HTTPError:
                logger.exception("Failed to create sub-task %s", task.summary)
                failed_tasks.append(task.summary)
            except Exception:  # pylint: disable=broad-exception-caught
                logger.exception(
                    "Unexpected error creating sub-task %s",
                    task.summary,
                )
                failed_tasks.append(task.summary)
        if failed_tasks:
            logger.warning(
                "Failed to create %d/%d tasks for %s",
                len(failed_tasks),
                len(all_tasks),
                parent_key,
            )

    def create_story_with_sub_tasks(self, story: Story) -> str | None:
        """Create a story with sub-tasks.

        Create a story and return the issue key.
        Create sub-tasks for the story.

        Parameters
        ----------
        story : Story
            Story to be created.

        Returns
        -------
        str | None
            The issue key of the created story
            or None if the story could not be created.

        """
        try:
            parent_key = self.create_story_within_epic(story)
            if not story.tasks:
                logger.warning(
                    "No tasks found for story %s",
                    story.summary,
                )
                return parent_key
            self.create_sub_tasks_in_story(all_tasks=story.tasks, parent_key=parent_key)
        except StoryCreationError:
            logger.exception("The story was not created.")
            return None
        except Exception:  # pylint: disable=broad-exception-caught
            logger.exception(
                "Unexpected error creating story %s",
                story.summary,
            )
            return None
        return parent_key

    def create_stories(self, stories: list[Story]) -> dict[str, str | None]:
        """Create stories with sub-tasks.

        Create stories and return the issue keys.
        Create sub-tasks for the stories.

        Parameters
        ----------
        stories : list[Story]
            Stories to be created.

        Returns
        -------
        dict[str, str | None]
            A dictionary mapping story summaries to issue keys.

        """
        results = {}
        for story in stories:
            issue_key = self.create_story_with_sub_tasks(story)
            results[story.summary] = issue_key

        success_count = sum(1 for key in results.values() if key is not None)
        logger.info(
            "Created %d/%d stories successfully",
            success_count,
            len(stories),
        )
        return results
