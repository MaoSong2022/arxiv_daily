"""Utility functions for JSON operations."""

import json
from typing import Any


def load_json(json_file: str) -> Any:
    """Load data from a JSON file.

    Args:
        json_file: Path to the JSON file to load.

    Returns:
        The data loaded from the JSON file.

    Raises:
        FileNotFoundError: If the file doesn't exist.
        json.JSONDecodeError: If the file contains invalid JSON.
    """
    with open(json_file, encoding="utf-8") as f:
        data = json.load(f)
    return data


def export_to_json(data: Any, json_file: str) -> None:
    """Export data to a JSON file.

    Args:
        data: The data to export.
        json_file: Path where to save the JSON file.

    Raises:
        OSError: If the file cannot be written.
    """
    with open(json_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
