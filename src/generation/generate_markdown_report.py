from typing import Dict, List, Any
from loguru import logger

from src.config.settings import settings


def generate_markdown_report(data: List[Dict[str, Any]], output_path: str) -> None:
    """
    Generate a markdown report that categorizes papers based on predefined classifiers.

    Args:
        data: List of paper data dictionaries
        output_path: Path where the markdown file will be saved

    Returns:
        None
    """
    logger.info("Generating markdown report...")
    # Initialize sections with empty lists
    sections = {}

    # Categorize papers
    for paper in data:
        title = paper.get("title", "")

        # Check if paper has pre-assigned classifiers
        classifiers = paper.get("classifiers", ["Unknown"])
        classifier = classifiers[0].lower()
        if classifier in sections:
            sections[classifier].append(paper)
        else:
            sections[classifier] = [paper]

    sub_sections_contents = {}

    for section, papers in sections.items():
        sub_section_content = ""
        if section in settings.filtered_categories:
            continue
        if not papers:  # Skip empty sections
            continue

        sub_section_content += f"### {section}\n"

        for paper in papers:
            title = paper.get("title", "No Title")
            pdf_url = paper.get("pdf_url", "")
            keywords = paper.get("keywords", [])
            comments = paper.get("comments", "")
            tldr = paper.get("tldr", "")

            sub_section_content += pdf_url + "\n"
            sub_section_content += "标题： " + title + "\n"

            if keywords:
                sub_section_content += "**Keywords:** " + ", ".join(keywords) + "\n"

            if comments:
                sub_section_content += f"**Comments:** {comments}\n"

            if tldr:
                sub_section_content += f"**TL;DR:** {tldr}\n"

            sub_section_content += "关键词： \n"
            sub_section_content += "简介： \n"

            sub_section_content += "\n\n"

        sub_sections_contents[section] = sub_section_content

    sections_contents = {}

    for sub_section, content in sub_sections_contents.items():
        section = settings.super_categories.get(sub_section, "Others")
        if section in sections_contents:
            sections_contents[section] += content
        else:
            sections_contents[section] = content
        sections_contents[section] += "\n\n"

    # Write to file
    with open(output_path, "w", encoding="utf-8") as f:
        for section, content in sections_contents.items():
            f.write(f"## {section}\n")
            f.write(content)
            f.write("\n\n")

    logger.info(f"Markdown report generated at {output_path}")
