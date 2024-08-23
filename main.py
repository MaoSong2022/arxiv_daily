import os
from typing import List, Dict, Any
from pathlib import Path
import datetime
from pytz import timezone

import arxiv
from loguru import logger
from rich import print

import utils


tz = timezone("US/Eastern")
logger.add("daily.log")


def retrieve_metadata(paper_id: str) -> Dict[str, Any]:
    """
    Retrieves metadata for the given list of paper IDs.

    Args:
    data (str): paper_id

    Returns:
    List[Dict[str, Any]]: A list of dictionaries containing metadata for each paper.

    Raises:
    None

    References:
    https://info.arxiv.org/help/api/user-manual.html#_details_of_atom_results_returned

    """

    client = arxiv.Client()

    search_results = client.results(arxiv.Search(id_list=[paper_id]))

    paper_metadata = []
    for index, result in enumerate(search_results):
        paper_metadata.append(
            {
                "entry_id": result.entry_id,
                "updated": str(result.updated),
                "published": str(result.published.astimezone(tz)),
                "title": result.title,
                "doi": result.doi,
                "authors": [str(author) for author in result.authors],
                "summary": result.summary,
                "journal_ref": result.journal_ref,
                "primary_category": result.primary_category,
                "categories": result.categories,
                "links": [str(link) for link in result.links],
                "pdf_url": result.pdf_url,
                "paper_id": paper_id,
            }
        )

    return paper_metadata


def query_yesterday_papers(category: str):
    client = arxiv.Client()

    now = datetime.datetime.now(tz)
    day_before_yesterday = now - datetime.timedelta(days=2)
    submitted_deadline = day_before_yesterday.replace(
        hour=14, minute=0, second=0, microsecond=0
    )
    submitted_deadline = submitted_deadline.astimezone(tz)
    logger.debug(f"submitted_deadline={str(submitted_deadline)}")

    results = []

    offset = 0
    max_results = 10

    while True:
        search_results = client.results(
            arxiv.Search(
                query=category,
                max_results=max_results,
                sort_by=arxiv.SortCriterion.LastUpdatedDate,
                sort_order=arxiv.SortOrder.Ascending,
            ),
            offset=offset,
        )
        logger.debug("fetched results.")

        for search_result in search_results:
            item = {
                "paper_id": search_result.get_short_id(),
                "paper_url": search_result.entry_id,
                "updated": search_result.updated.astimezone(tz),
                "published": search_result.published.astimezone(tz),
                "title": search_result.title,
                "abstract": search_result.summary,
                "doi": search_result.doi,
                "authors": [str(author) for author in search_result.authors],
                "comments": search_result.comment,
                "journal_ref": search_result.journal_ref,
                "primary_category": search_result.primary_category,
                "categories": search_result.categories,
                "links": [str(link) for link in search_result.links],
                "pdf_url": search_result.pdf_url,
            }

            logger.debug(f"title={item['title']}")

            update_time = item["updated"]
            logger.debug(f"update_time={item['updated']}")
            # we get the papers that submitted in the range (now_day-2^14:00, now_day-1^14:00, EST)
            # https://info.arxiv.org/help/availability.html

            if update_time > submitted_deadline:
                break

            item["updated"] = str(item["updated"])
            item["published"] = str(item["published"])
            results.append(item)

        offset += max_results

    return results


def main():
    today = datetime.date.today()
    yesterday_papers = query_yesterday_papers("cs.CV")
    utils.export_to_json(yesterday_papers, f"output/{str(today)}.json")


if __name__ == "__main__":
    main()
