from typing import List, Dict, Any
from tqdm import tqdm
from loguru import logger
import os
import litellm
import openai

from src.config.settings import settings


def add_paper_summaries(
    papers_by_category: Dict[str, List[Dict[str, Any]]],
    model_name: str = "ollama/qwen2.5:32b",
) -> Dict[str, List[Dict[str, Any]]]:
    """
    Add TL;DR summaries and keywords to each paper using Ollama.

    Args:
        papers_by_category: Dictionary mapping categories to lists of paper data
        model_name: Name of the Ollama model to use

    Returns:
        Updated dictionary with TL;DR and keywords added to each paper
    """
    logger.info("Adding TL;DR summaries and keywords to papers...")

    for category, papers in papers_by_category.items():
        logger.info(f"Processing {len(papers)} papers in category {category}")

        for paper in tqdm(
            papers, desc=f"Processing papers in {category}", unit="paper"
        ):
            # Create prompt for Ollama
            user_prompt = settings.prompt_template.format(
                title=paper["title"],
                abstract=paper["abstract"],
                classifiers=", ".join(settings.classifiers),
            )
            logger.debug(f"User prompt:\n {user_prompt}")

            try:
                if "ollama" in model_name:
                    response = litellm.completion(
                        model=f"{model_name}",
                        messages=[{"role": "user", "content": user_prompt}],
                    )
                else:
                    client = openai.OpenAI(
                        api_key=os.getenv("OPENAI_API_KEY"),
                        base_url=os.getenv("API_BASE_URL"),
                    )
                    response = client.chat.completions.create(
                        model=f"{model_name}",
                        messages=[{"role": "user", "content": user_prompt}],
                    )
                response_text = response.choices[0].message.content

                logger.debug(f"Response:\n {response_text}")
                # Extract TL;DR, keywords, and classifier from response
                tldr = ""
                keywords = []
                paper_classifiers = []

                if "TL;DR:" in response_text:
                    tldr_section = (
                        response_text.split("TL;DR:")[1].split("Keywords:")[0].strip()
                    )
                    tldr = tldr_section

                if "Keywords:" in response_text:
                    keywords_text = response_text.split("Keywords:")[1]
                    if "Classifier:" in keywords_text:
                        keywords_section = keywords_text.split("Classifier:")[0].strip()
                    else:
                        keywords_section = keywords_text.strip()
                    # Clean up keywords and convert to list
                    keywords = [k.strip() for k in keywords_section.split(",")]

                if "Classifier:" in response_text:
                    classifiers_section = response_text.split("Classifier:")[1].strip()
                    # Clean up classifiers and convert to list
                    paper_classifiers = [
                        c.strip() for c in classifiers_section.split(",")
                    ]

                # Add to paper data
                paper["tldr"] = tldr
                paper["keywords"] = keywords
                paper["classifiers"] = paper_classifiers

                logger.debug("================================================")
                logger.debug(f"Added summary for paper: {paper['paper_id']}")
                logger.debug(f"Paper title: {paper['title']}")
                logger.debug(f"Paper tldr: {paper['tldr']}")
                logger.debug(f"Paper keywords: {paper['keywords']}")
                logger.debug(f"Paper classifiers: {paper['classifiers']}")
                logger.debug("================================================")
            except Exception as e:
                logger.error(f"Error processing paper {paper['paper_id']}: {str(e)}")
                paper["tldr"] = ""
                paper["keywords"] = []
                paper["classifiers"] = ["error"]

    return papers_by_category
