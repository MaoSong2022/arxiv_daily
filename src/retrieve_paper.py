from typing import List, Dict, Any, Optional
import datetime
import requests
from loguru import logger


from bs4 import BeautifulSoup

import arxiv

from src import config


def from_cool_paper(
    categories: List[str],
    date_day: datetime.date = datetime.date.today(),
) -> Dict[str, List[Dict[str, Any]]]:
    """
    Query papers.cool for papers in specified categories.

    Args:
        categories: List of arXiv categories to query
        date_day: The date to filter papers by (defaults to today)

    Returns:
        Dictionary mapping categories to lists of paper data dictionaries
    """
    all_results: Dict[str, List[Dict[str, Any]]] = {
        category: [] for category in categories
    }
    show = 1000

    # Format date for URL
    for category in categories:
        date_str = date_day.strftime("%Y-%m-%d")
        url = f"https://papers.cool/arxiv/{category}?date={date_str}&show={show}"

        try:
            response = requests.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")

            # Find all paper entries
            paper_entries = soup.find_all("div", class_="panel paper")

            for entry in paper_entries:
                # Extract paper ID from div id
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
                    categories_list = [
                        subject.text.strip() for subject in subject_links
                    ]

                # Extract publish date
                date_elem = entry.find("p", class_="date")
                publish_date = ""
                if date_elem:
                    date_text = date_elem.text.strip()
                    if "Publish" in date_text:
                        publish_date = date_text.split("Publish")[1].strip(": ")

                # Extract keywords
                keywords = entry.get("keywords", "").split(",")

                # Create paper data dictionary
                paper_data = {
                    "paper_id": paper_id,
                    "paper_url": f"https://arxiv.org/abs/{paper_id}",
                    "updated": publish_date,  # Using publish date as updated date
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

                # Add to results
                all_results[category].append(paper_data)

            logger.info(
                f"Retrieved {len(all_results[category])} papers from papers.cool for category {category}"
            )

        except requests.RequestException as e:
            logger.error(
                f"Error fetching papers from papers.cool for category {category}: {e}"
            )
            continue
        except Exception as e:
            logger.error(
                f"Error parsing papers from papers.cool for category {category}: {e}"
            )
            continue

    return all_results


def from_arxiv(
    categories: List[str],
    max_results: int = 500,
    date_day: datetime.date = datetime.date.today(),
) -> Dict[str, List[Dict[str, Any]]]:
    """
    Query arXiv for papers submitted yesterday in specified categories.

    Args:
        categories: List of arXiv categories to query
        max_results: Maximum number of results to return per category
        date_day: The date to filter papers by (defaults to today)

    Returns:
        Dictionary mapping categories to lists of paper data dictionaries
    """
    client = arxiv.Client()
    all_results: Dict[str, List[Dict[str, Any]]] = {
        category: [] for category in categories
    }

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
        f"target data start: {target_day_start}, target_dat_end: {target_day_end}"
    )

    # Check if the paper was updated on the target date
    date_range = (target_day_start, target_day_end)
    logger.debug(f"Date range: ({str(date_range[0])}, {str(date_range[1])})")

    for category in categories:
        logger.info(f"Processing category: {category}")

        search_results = client.results(
            arxiv.Search(
                query=f"cat:{category}",
                max_results=max_results,
                sort_by=arxiv.SortCriterion.LastUpdatedDate,
                sort_order=arxiv.SortOrder.Descending,
            ),
        )
        logger.info("Successfully fetched results from arxiv")

        category_results = []
        for search_result in search_results:
            item = {
                "paper_id": search_result.get_short_id(),
                "paper_url": search_result.entry_id,
                "updated": search_result.updated.astimezone(
                    datetime.timezone(datetime.timedelta(hours=-5))
                ),  # EST
                "published": search_result.published.astimezone(
                    datetime.timezone(datetime.timedelta(hours=-5))
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

            logger.debug(
                f"Paper {item['paper_id']} published day: {item['published']}, updated day: {item['updated']}"
            )

            # Stop processing once we reach papers outside our date range
            if item["updated"] <= target_day_start:
                logger.debug(
                    f"Skipping paper from {str(item['updated'])} as it's outside our target date range"
                )
                break

            # Skip papers that weren't published yesterday or if the update is more than 7 days after publication
            if item["published"] <= target_day_start:
                logger.debug(
                    f"Skipping paper {item['paper_id']} as it's published before the target date range"
                )
                continue

            if item["primary_category"] not in categories:
                logger.debug(
                    f"Skipping paper {item['paper_id']} with primary category {item['primary_category']}"
                )
                continue

            # Convert datetime objects to strings for JSON serialization
            item["updated"] = str(item["updated"])
            item["published"] = str(item["published"])
            category_results.append(item)

        logger.info(
            f"Retrieved {len(category_results)} papers from category {category}"
        )

        all_results[category] = category_results

    return all_results


def query_single_paper(query: str) -> Optional[Dict[str, Any]]:
    """
    Query arXiv for a single paper by title or ID.

    Args:
        query: Paper title or arXiv ID to search for

    Returns:
        Dictionary containing paper data if found, None otherwise
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
