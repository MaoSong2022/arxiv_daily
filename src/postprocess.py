from typing import List, Dict, Any, Set
import datetime
import os
from loguru import logger

from src import utils


def remove_duplicates_by_id(
    data: Dict[str, List[Dict[str, Any]]],
) -> Dict[str, List[Dict[str, Any]]]:
    """
    Remove duplicate papers based on paper_id across different categories.

    Args:
        data: Dictionary mapping categories to lists of paper data dictionaries

    Returns:
        Dictionary with duplicate papers removed across categories
    """
    processed_paper_ids: Set[str] = set()
    result: Dict[str, List[Dict[str, Any]]] = {}

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
    data: Dict[str, List[Dict[str, Any]]], current_date: datetime.date, output_file: str
) -> Dict[str, List[Dict[str, Any]]]:
    prev_day = current_date - datetime.timedelta(days=1)
    while prev_day.weekday() >= 5:  # 5 = Saturday, 6 = Sunday
        prev_day -= datetime.timedelta(days=1)

    output_dir = os.path.dirname(os.path.dirname(output_file))
    prev_day_json_file = os.path.join(
        output_dir, str(prev_day.strftime("%Y-%m")), f"{str(prev_day)}.json"
    )
    logger.debug(f"previous json file: {prev_day_json_file}")
    prev_day_data = utils.load_json(prev_day_json_file)
    prev_date_uuid = [x["paper_id"] for value in prev_day_data.values() for x in value]
    data = {
        key: [x for x in value if x["paper_id"] not in prev_date_uuid]
        for key, value in data.items()
    }
    return data
