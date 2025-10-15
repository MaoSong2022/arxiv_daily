"""Paper retrieval functions from arXiv and papers.cool."""

import datetime
from typing import Any, Dict, List, Optional

import arxiv
import pytz
import requests
from bs4 import BeautifulSoup
from loguru import logger

from src import config


def _extract_paper_data_from_cool_paper(
    entry: BeautifulSoup, category: str
) -> dict[str, Any]:
    """Extract paper data from a papers.cool entry.

    Args:
        entry: BeautifulSoup element containing paper data.
        category: arXiv category for the paper.

    Returns:
        Dictionary containing extracted paper data.
    """
    paper_id = entry.get("id", "")

    # Extract title
    title_elem = entry.find("a", class_="title-link")
    title = title_elem.text.strip() if title_elem else ""

    # Extract authors
    authors_elem = entry.find("p", class_="authors")
    authors = []
    if authors_elem:
        author_links = authors_elem.find_all("a", class_="author")
        authors = [author.text.strip() for author in author_links]

    # Extract abstract/summary
    summary_elem = entry.find("p", class_="summary")
    abstract = summary_elem.text.strip() if summary_elem else ""

    # Extract subjects/categories
    subjects_elem = entry.find("p", class_="subjects")
    categories_list = []
    if subjects_elem:
        subject_links = subjects_elem.find_all("a", class_="subject-1")
        categories_list = [subject.text.strip() for subject in subject_links]

    # Extract publish date
    date_elem = entry.find("p", class_="date")
    publish_date = ""
    if date_elem:
        date_text = date_elem.text.strip()
        if "Publish" in date_text:
            publish_date = date_text.split("Publish")[1].strip(": ")

    # Extract keywords
    keywords = entry.get("keywords", "").split(",")

    return {
        "paper_id": paper_id,
        "paper_url": f"https://arxiv.org/abs/{paper_id}",
        "updated": publish_date,
        "published": publish_date,
        "title": title,
        "abstract": abstract,
        "doi": "",  # papers.cool doesn't provide this
        "authors": authors,
        "comments": "",  # papers.cool doesn't provide this
        "journal_ref": "",  # papers.cool doesn't provide this
        "primary_category": category,
        "categories": categories_list or [category],
        "links": [
            f"https://arxiv.org/abs/{paper_id}",
            f"https://arxiv.org/pdf/{paper_id}.pdf",
        ],
        "pdf_url": f"https://arxiv.org/pdf/{paper_id}.pdf",
        "keywords": keywords,
    }


def _fetch_papers_from_cool_paper_category(
    category: str, date_day: datetime.date, max_results: int
) -> list[dict[str, Any]]:
    """Fetch papers from papers.cool for a single category.

    Args:
        category: arXiv category to query.
        date_day: Date to filter papers by.
        max_results: Maximum number of results to return.

    Returns:
        List of paper data dictionaries.

    Raises:
        requests.RequestException: If the HTTP request fails.
        Exception: If parsing fails.
    """
    date_str = date_day.strftime("%Y-%m-%d")
    url = f"https://papers.cool/arxiv/{category}?date={date_str}&show={max_results}"

    response = requests.get(url, timeout=30)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    paper_entries = soup.find_all("div", class_="panel paper")

    papers = []
    for entry in paper_entries:
        try:
            paper_data = _extract_paper_data_from_cool_paper(entry, category)
            papers.append(paper_data)
        except Exception as e:
            logger.warning(f"Error extracting paper data: {e}")
            continue

    return papers


def from_cool_paper(
    categories: list[str],
    date_day: datetime.date = datetime.date.today(),
    max_results: int = 1000,
) -> dict[str, list[dict[str, Any]]]:
    """Query papers.cool for papers in specified categories.

    Args:
        categories: List of arXiv categories to query.
        date_day: The date to filter papers by (defaults to today).
        max_results: Maximum number of results to return per category.

    Returns:
        Dictionary mapping categories to lists of paper data dictionaries.
    """
    all_results: dict[str, list[dict[str, Any]]] = {
        category: [] for category in categories
    }

    for category in categories:
        try:
            papers = _fetch_papers_from_cool_paper_category(
                category, date_day, max_results
            )
            all_results[category] = papers

            logger.info(
                f"Retrieved {len(papers)} papers from papers.cool for category {category}"
            )

        except requests.RequestException as e:
            logger.error(
                f"Error fetching papers from papers.cool for category {category}: {e}"
            )
        except Exception as e:
            logger.error(
                f"Error parsing papers from papers.cool for category {category}: {e}"
            )

    return all_results


def _create_paper_dict_from_arxiv_result(result: arxiv.Result) -> dict[str, Any]:
    """Create a paper dictionary from an arXiv result.

    Args:
        result: arXiv result object.

    Returns:
        Dictionary containing paper data.
    """
    est_tz = pytz.timezone("America/New_York")

    return {
        "paper_id": result.get_short_id(),
        "paper_url": result.entry_id,
        "updated": result.updated.astimezone(est_tz),
        "published": result.published.astimezone(est_tz),
        "title": result.title,
        "abstract": result.summary,
        "doi": result.doi,
        "authors": [str(author) for author in result.authors],
        "comments": result.comment,
        "journal_ref": result.journal_ref,
        "primary_category": result.primary_category,
        "categories": result.categories,
        "links": [str(link) for link in result.links],
        "pdf_url": result.pdf_url,
    }




def _fetch_papers_from_arxiv_category(
    category: str,
    max_results: int,
    target_day_start: datetime.datetime,
    target_day_end: datetime.datetime,
    categories: list[str],
) -> list[dict[str, Any]]:
    """Fetch papers from arXiv for a single category.

    Args:
        category: arXiv category to query.
        max_results: Maximum number of results to return.
        target_day_start: Start of target date range.
        target_day_end: End of target date range.
        categories: List of valid categories.

    Returns:
        List of paper data dictionaries.
    """
    client = arxiv.Client()

    search_results = client.results(
        arxiv.Search(
            query=f"cat:{category}",
            max_results=max_results,
            sort_by=arxiv.SortCriterion.LastUpdatedDate,
            sort_order=arxiv.SortOrder.Descending,
        ),
    )

    category_results = []
    for search_result in search_results:
        paper = _create_paper_dict_from_arxiv_result(search_result)

        logger.debug(
            f"Paper {paper['paper_id']} published: {paper['published']}, updated: {paper['updated']}"
        )

        # Check if paper is in date range
        if paper["published"] < target_day_start:
            continue

        # Skip papers with invalid primary category
        if paper["primary_category"] not in categories:
            logger.debug(
                f"Skipping paper {paper['paper_id']} with primary category {paper['primary_category']}"
            )
            continue

        # Convert datetime objects to strings for JSON serialization
        paper["updated"] = str(paper["updated"])
        paper["published"] = str(paper["published"])
        category_results.append(paper)

    return category_results


def from_arxiv(
    categories: list[str],
    max_results: int = 500,
    date_day: datetime.date = datetime.date.today(),
) -> dict[str, list[dict[str, Any]]]:
    """Query arXiv for papers submitted in specified categories.

    Args:
        categories: List of arXiv categories to query.
        max_results: Maximum number of results to return per category.
        date_day: The date to filter papers by (defaults to today).

    Returns:
        Dictionary mapping categories to lists of paper data dictionaries.
    """
    all_results: dict[str, list[dict[str, Any]]] = {
        category: [] for category in categories
    }

    # Calculate date range
    updated_day_delta = config.day_delta[date_day.weekday()]
    target_day_start = datetime.datetime.combine(
        date_day - datetime.timedelta(days=updated_day_delta[0]),
        datetime.time(10, 0),
    ).replace(tzinfo=datetime.timezone(datetime.timedelta(hours=-5)))
    target_day_end = datetime.datetime.combine(
        date_day - datetime.timedelta(days=updated_day_delta[1]),
        datetime.time(14, 0),
    ).replace(tzinfo=datetime.timezone(datetime.timedelta(hours=-5)))

    logger.info(
        f"Target date start: {target_day_start}, target date end: {target_day_end}"
    )

    for category in categories:
        logger.info(f"Processing category: {category}")

        try:
            category_results = _fetch_papers_from_arxiv_category(
                category, max_results, target_day_start, target_day_end, categories
            )
            all_results[category] = category_results

            logger.info(
                f"Retrieved {len(category_results)} papers from category {category}"
            )

        except Exception as e:
            logger.error(f"Error processing category {category}: {e}")
            all_results[category] = []

    return all_results


def query_single_paper(query: str) -> Optional[dict[str, Any]]:
    """Query arXiv for a single paper by title or ID.

    Args:
        query: Paper title or arXiv ID to search for.

    Returns:
        Dictionary containing paper data if found, None otherwise.
    """
    client = arxiv.Client()

    # Check if query is an arXiv ID
    if query.replace(".", "").isdigit() or (
        "." in query and len(query.split(".")) == 2
    ):
        search_query = f"id:{query}"
    else:
        search_query = f'ti:"{query}"'

    try:
        search_results = client.results(arxiv.Search(query=search_query, max_results=1))

        # Get first result
        search_result = next(search_results, None)

        if search_result is None:
            logger.warning(f"No paper found for query: {query}")
            return None

        item = {
            "paper_id": search_result.get_short_id(),
            "paper_url": search_result.entry_id,
            "updated": str(
                search_result.updated.astimezone(
                    datetime.timezone(datetime.timedelta(hours=-5))
                )
            ),  # EST
            "published": str(
                search_result.published.astimezone(
                    datetime.timezone(datetime.timedelta(hours=-5))
                )
            ),  # EST
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

        logger.info(f"Successfully retrieved paper: {item['title']}")
        return item

    except Exception as e:
        logger.error(f"Error querying arXiv: {str(e)}")
        return None
