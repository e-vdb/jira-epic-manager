"""Utils module."""
from __future__ import annotations

import json
from pathlib import Path


def load_json(file_path: str | Path) -> dict:
    """Load a JSON file."""
    filepath = Path(file_path) if isinstance(file_path, str) else file_path
    with filepath.open(encoding="utf-8") as f:
        return json.load(f)
