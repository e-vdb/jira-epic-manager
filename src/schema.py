"""Schema module."""

from __future__ import annotations

from typing import TYPE_CHECKING

from pydantic import BaseModel, Field

from src.utils import load_json

if TYPE_CHECKING:
    from pathlib import Path


class Task(BaseModel):
    """Task model."""

    summary: str = Field(..., title="Summary")
    description: str = Field(..., title="Description")
    assignee_id: str | None = Field(None, title="Assignee ID")


class Story(BaseModel):
    """Story model."""

    summary: str = Field(..., title="Summary")
    description: str = Field(..., title="Description")
    tasks: list[Task] | None = Field(..., title="Tasks")
    assignee_id: str | None = Field(None, title="Assignee ID")

    @classmethod
    def from_json_file(cls, filepath: str | Path) -> Story:
        """Load a Story from a JSON file."""
        data = load_json(filepath)
        return cls.model_validate(data)
