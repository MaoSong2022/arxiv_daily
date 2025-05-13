from typing import List, Dict, Any, Set

from src.config.settings import settings


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
