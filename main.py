import os
from typing import List, Dict, Any
from pathlib import Path
from dotenv import load_dotenv
import datetime
from pytz import timezone
import ollama
import tqdm

import arxiv
from loguru import logger
from zhipuai import ZhipuAI

import utils

load_dotenv()
ZHIPU_API_KEY = os.getenv("ZHIPU_API_KEY")
client = ZhipuAI(api_key=ZHIPU_API_KEY)


logger.remove()
logger.add("daily.log", mode="w")
logger.add(sys.stdout, level="INFO")


def add_tldr(json_data):
    logger.info("adding TLDR for extracted papers.")
    for item in tqdm.tqdm(json_data):
        response = client.chat.completions.create(
            model="glm-4-flash",
            messages=[
                {
                    "role": "system",
                    "content": "你是一个专业的科研助手，基于以下给定的一篇论文的摘要，用一句话总结这篇论文，并提炼出三到五个关键词。使用中文回答",
                },
                {
                    "role": "user",
                    "content": item["abstract"],
                },
            ],
        )

        tldr = str(response.choices[0].message.content)
        logger.debug(f"tldr: {tldr}")
        item["tldr"] = tldr


def query_yesterday_papers(
    category: str,
    max_results: int = 500,
    delta_day: int = 2,
):
    logger.info(f"processing category: {category}")
    client = arxiv.Client()

    now = datetime.datetime.now(tz)
    day_before_yesterday = now - datetime.timedelta(days=delta_day)
    submitted_deadline = day_before_yesterday.replace(
        hour=14, minute=0, second=0, microsecond=0
    )
    submitted_deadline = submitted_deadline.astimezone(tz)
    logger.debug(f"submitted_deadline={str(submitted_deadline)}")

    results = []

    search_results = client.results(
        arxiv.Search(
            query=f"all:{category}",
            max_results=max_results,
            sort_by=arxiv.SortCriterion.LastUpdatedDate,
            sort_order=arxiv.SortOrder.Descending,
        ),
    )
    logger.debug("successfully fetching results.")

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
        logger.debug(f"paper title={item['title']}")
        logger.debug(f"updated={item['updated']}")

        update_time = item["updated"]
        logger.debug(f"update_time={item['updated']}")
        # we get the papers that submitted in the range (now_day-2^14:00, now_day-1^14:00, EST)
        # https://info.arxiv.org/help/availability.html

        logger.debug(f"updated_day = {updated_day}")

        if update_time < submitted_deadline:
            break

        item["updated"] = str(item["updated"])
        item["published"] = str(item["published"])
        results.append(item)

    return results


def remove_duplicates_by_id(data):
    seen_ids = set()
    unique_data = []
    for item in data:
        if item["paper_id"] in seen_ids:
            continue

        seen_ids.add(item["paper_id"])
        unique_data.append(item)
    return unique_data


def main():
    # step 1: determine the deadline for retrieval
    today = datetime.date.today()
    week_day = today.weekday()
    logger.info(f"today: {today}, week_day: {week_day}")

    delta_days = [4, 4, 2, 2, 2, None, None]
    # https://info.arxiv.org/help/availability.html Announcement Schedule
    delta_day = delta_days[week_day]
    if not delta_days:
        logger.error("Arxiv has no announcements on Saturday or Sunday")
        return

    categories = ["cs.LG", "cs.AI", "cs.CV", "cs.CL"]

    # step 2: retrieve results
    result = []
    for category in categories:
        papers = query_yesterday_papers(category, delta_day=delta_day)
        result.extend(papers)
        logger.info(f"retrieve {len(papers)} from category {category}")

    # step 3: remove duplicates
    result = remove_duplicates_by_id(result)
    logger.info(f"there are {len(result)} unique papers.")
    # Step 4: use LLM to add TLDR for better filtering
    add_tldr(result)

    utils.export_to_json(result, f"output/{str(today)}.json")


if __name__ == "__main__":
    main()
