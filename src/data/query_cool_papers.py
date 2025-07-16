from typing import List, Dict, Any
import datetime
from bs4 import BeautifulSoup
import requests
from loguru import logger


def query_cool_papers(
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
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find all paper entries
            paper_entries = soup.find_all('div', class_='panel paper')
            
            for entry in paper_entries:
                # Extract paper ID from div id
                paper_id = entry.get('id', '')
                
                # Extract title
                title_elem = entry.find('a', class_='title-link')
                title = title_elem.text.strip() if title_elem else ""
                
                # Extract authors
                authors_elem = entry.find('p', class_='authors')
                authors = []
                if authors_elem:
                    author_links = authors_elem.find_all('a', class_='author')
                    authors = [author.text.strip() for author in author_links]
                
                # Extract abstract/summary
                summary_elem = entry.find('p', class_='summary')
                abstract = summary_elem.text.strip() if summary_elem else ""
                
                # Extract subjects/categories
                subjects_elem = entry.find('p', class_='subjects')
                categories_list = []
                if subjects_elem:
                    subject_links = subjects_elem.find_all('a', class_='subject-1')
                    categories_list = [subject.text.strip() for subject in subject_links]
                
                # Extract publish date
                date_elem = entry.find('p', class_='date')
                publish_date = ""
                if date_elem:
                    date_text = date_elem.text.strip()
                    if "Publish" in date_text:
                        publish_date = date_text.split("Publish")[1].strip(": ")
                
                # Extract keywords
                keywords = entry.get('keywords', '').split(',')
                
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
                        f"https://arxiv.org/pdf/{paper_id}.pdf"
                    ],
                    "pdf_url": f"https://arxiv.org/pdf/{paper_id}.pdf",
                    "keywords": keywords,
                }
                
                # Add to results
                all_results[category].append(paper_data)
                
            logger.info(f"Retrieved {len(all_results[category])} papers from papers.cool for category {category}")
            
        except requests.RequestException as e:
            logger.error(f"Error fetching papers from papers.cool for category {category}: {e}")
            continue
        except Exception as e:
            logger.error(f"Error parsing papers from papers.cool for category {category}: {e}")
            continue

    return all_results
