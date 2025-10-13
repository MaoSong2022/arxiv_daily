"""Paper summarization functions using AI models."""

import os
from typing import Any, Dict, List

import litellm
import openai
from loguru import logger
from tqdm import tqdm

from src import config


def _create_summarization_prompt(paper: dict[str, Any]) -> str:
    """Create a summarization prompt for a paper.

    Args:
        paper: Paper data dictionary.

    Returns:
        Formatted prompt string.
    """
    return config.prompt_template.format(
        title=paper["title"],
        abstract=paper["abstract"],
        classifiers=", ".join(config.classifiers),
    )


def _call_ai_model(prompt: str, model_name: str) -> str:
    """Call the AI model with the given prompt.

    Args:
        prompt: The prompt to send to the model.
        model_name: Name of the model to use.

    Returns:
        Response text from the model.

    Raises:
        Exception: If the API call fails.
    """
    if "ollama" in model_name:
        response = litellm.completion(
            model=model_name,
            messages=[{"role": "user", "content": prompt}],
            timeout=60,
        )
    else:
        client = openai.OpenAI(
            api_key=os.getenv("OPENAI_API_KEY"),
            base_url=os.getenv("API_BASE_URL"),
        )
        response = client.chat.completions.create(
            model=model_name,
            messages=[{"role": "user", "content": prompt}],
            timeout=60,
        )

    if not response.choices or not response.choices[0].message.content:
        raise ValueError("Empty response from model")

    return response.choices[0].message.content


def _parse_ai_response(response_text: str) -> tuple[str, list[str], list[str]]:
    """Parse AI response to extract TL;DR, keywords, and classifiers.

    Args:
        response_text: Raw response text from AI model.

    Returns:
        Tuple of (tldr, keywords, classifiers).
    """
    tldr = ""
    keywords = []
    classifiers = []

    if "TL;DR:" in response_text:
        tldr_section = response_text.split("TL;DR:")[1]
        if "Keywords:" in tldr_section:
            tldr = tldr_section.split("Keywords:")[0].strip()
        else:
            tldr = tldr_section.strip()

    if "Keywords:" in response_text:
        keywords_text = response_text.split("Keywords:")[1]
        if "Classifier:" in keywords_text:
            keywords_section = keywords_text.split("Classifier:")[0].strip()
        else:
            keywords_section = keywords_text.strip()
        keywords = [k.strip() for k in keywords_section.split(",") if k.strip()]

    if "Classifier:" in response_text:
        classifiers_section = response_text.split("Classifier:")[1].strip()
        classifiers = [c.strip() for c in classifiers_section.split(",") if c.strip()]

    return tldr, keywords, classifiers


def _process_single_paper(
    paper: dict[str, Any], model_name: str
) -> dict[str, Any]:
    """Process a single paper to add summaries and keywords.

    Args:
        paper: Paper data dictionary.
        model_name: Name of the model to use.

    Returns:
        Updated paper dictionary with summaries.
    """
    try:
        prompt = _create_summarization_prompt(paper)
        logger.debug(f"User prompt:\n{prompt}")

        response_text = _call_ai_model(prompt, model_name)
        logger.debug(f"Response:\n{response_text}")

        tldr, keywords, classifiers = _parse_ai_response(response_text)

        # Update paper with extracted data
        paper["tldr"] = tldr
        paper["keywords"] = keywords
        paper["classifiers"] = classifiers

        logger.debug(f"Added summary for paper: {paper['paper_id']}")
        logger.debug(f"TL;DR: {tldr}")
        logger.debug(f"Keywords: {keywords}")
        logger.debug(f"Classifiers: {classifiers}")

    except Exception as e:
        logger.error(f"Error processing paper {paper['paper_id']}: {str(e)}")
        paper["tldr"] = ""
        paper["keywords"] = []
        paper["classifiers"] = ["error"]

    return paper


def add_paper_summaries(
    papers_by_category: dict[str, list[dict[str, Any]]],
    model_name: str = "ollama/qwen2.5:32b",
) -> dict[str, list[dict[str, Any]]]:
    """Add TL;DR summaries and keywords to each paper using AI models.

    Args:
        papers_by_category: Dictionary mapping categories to lists of paper data.
        model_name: Name of the model to use for summarization.

    Returns:
        Updated dictionary with TL;DR and keywords added to each paper.
    """
    logger.info("Adding TL;DR summaries and keywords to papers...")

    for category, papers in papers_by_category.items():
        logger.info(f"Processing {len(papers)} papers in category {category}")

        for paper in tqdm(
            papers, desc=f"Processing papers in {category}", unit="paper"
        ):
            _process_single_paper(paper, model_name)

    return papers_by_category
