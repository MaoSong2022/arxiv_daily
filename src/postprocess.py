"""Post-processing functions for paper data."""

import datetime
import os
from pathlib import Path
from typing import Any, Dict, List, Set

from loguru import logger

from src import utils


def remove_duplicates_by_id(
    data: dict[str, list[dict[str, Any]]],
) -> dict[str, list[dict[str, Any]]]:
    """Remove duplicate papers based on paper_id across different categories.

    Args:
        data: Dictionary mapping categories to lists of paper data dictionaries.

    Returns:
        Dictionary with duplicate papers removed across categories.
    """
    processed_paper_ids: set[str] = set()
    result: dict[str, list[dict[str, Any]]] = {}

    # Initialize result dictionary with empty lists for each category
    for category in data:
        result[category] = []

    # Process each category
    for category, papers in data.items():
        for paper in papers:
            if paper["paper_id"] in processed_paper_ids:
                continue

            processed_paper_ids.add(paper["paper_id"])
            result[category].append(paper)

    return result


def remove_by_previous_day(
    data: dict[str, list[dict[str, Any]]], current_date: datetime.date, output_file: str
) -> dict[str, list[dict[str, Any]]]:
    """Remove papers that were already processed on the previous business day.

    Args:
        data: Dictionary mapping categories to lists of paper data.
        current_date: Current date to calculate previous business day from.
        output_file: Path to current output file to determine directory structure.

    Returns:
        Dictionary with papers from previous day removed.
    """
    # Calculate previous business day
    prev_day = current_date - datetime.timedelta(days=1)
    while prev_day.weekday() >= 5:  # 5 = Saturday, 6 = Sunday
        prev_day -= datetime.timedelta(days=1)

    # Construct path to previous day's file
    output_dir = Path(output_file).parent.parent
    prev_day_json_file = output_dir / prev_day.strftime("%Y-%m") / f"{prev_day}.json"

    logger.debug(f"Checking for previous day file: {prev_day_json_file}")

    if not prev_day_json_file.exists():
        logger.debug("No previous day file found, returning data unchanged")
        return data

    try:
        prev_day_data = utils.load_json(str(prev_day_json_file))
        prev_date_paper_ids = {
            paper["paper_id"] for papers in prev_day_data.values() for paper in papers
        }

        # Filter out papers that were already processed
        filtered_data = {
            category: [
                paper
                for paper in papers
                if paper["paper_id"] not in prev_date_paper_ids
            ]
            for category, papers in data.items()
        }

        removed_count = sum(
            len(papers) - len(filtered_data[category])
            for category, papers in data.items()
        )

        if removed_count > 0:
            logger.info(
                f"Removed {removed_count} papers that were already processed on {prev_day}"
            )

        return filtered_data

    except Exception as e:
        logger.error(f"Error processing previous day data: {str(e)}")
        logger.warning("Returning data unchanged due to error")
        return data
