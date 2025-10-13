"""Main entry point for the ArXiv Daily Paper Tracker."""

import argparse
import datetime
import json
import os
import sys
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from loguru import logger

from src import (
    config,
    html_report,
    markdown_report,
    postprocess,
    retrieve_paper,
    summarize,
    utils,
)

# Load environment variables
load_dotenv()

# Set environment variables for LLM
api_key = os.getenv("OPENAI_API_KEY")
api_base_url = os.getenv("API_BASE_URL")

if not api_key:
    logger.warning("OPENAI_API_KEY not found in environment variables")
if not api_base_url:
    logger.warning("API_BASE_URL not found in environment variables")

os.environ["OPENAI_API_KEY"] = api_key or ""
os.environ["API_BASE_URL"] = api_base_url or ""

# Configure logging
logger.remove()
logger.add(f"logs/daily_{datetime.date.today().strftime('%Y-%m-%d')}.log", mode="w")
logger.add(sys.stdout, level="INFO")


def parse_args() -> argparse.Namespace:
    """Parse command line arguments.

    Returns:
        Parsed command line arguments.
    """
    parser = argparse.ArgumentParser(description="ArXiv paper collector and reporter")
    parser.add_argument(
        "--output_path",
        type=str,
        default="output",
        help="Path to save the output files",
    )
    parser.add_argument(
        "--retrieve",
        action="store_true",
        help="Retrieve papers again even if output file exists",
    )
    parser.add_argument("--html", action="store_true", help="Regenerate HTML report")
    parser.add_argument(
        "--markdown", action="store_true", help="Regenerate markdown report"
    )
    parser.add_argument(
        "--resummarize", action="store_true", help="Regenerate summaries for papers"
    )
    parser.add_argument(
        "--date",
        type=str,
        help="Date to collect papers for (YYYY-MM-DD format). Defaults to today if not provided.",
    )
    parser.add_argument(
        "--model",
        type=str,
        default="ollama/qwen2.5:32b",
        help="Model name to use for generating summaries",
    )
    parser.add_argument(
        "--source",
        type=str,
        choices=["arxiv", "cool_paper"],
        default="arxiv",
        help="Source to query papers from: 'arxiv' or 'cool_paper'",
    )
    return parser.parse_args()


def setup_output_directories(
    output_path: str, target_date: datetime.date
) -> tuple[Path, Path, Path, Path]:
    """Set up output directories and file paths.

    Args:
        output_path: Base output directory path.
        target_date: Target date for file naming.

    Returns:
        Tuple of (output_file, selected_paper_file, html_file, markdown_file) paths.
    """
    output_path_obj = Path(output_path)
    output_path_obj.mkdir(exist_ok=True)

    target_month = target_date.strftime("%Y-%m")
    output_dir = output_path_obj / target_month
    output_dir.mkdir(exist_ok=True)

    output_file = output_dir / f"{target_date}.json"
    selected_paper_file = output_dir / f"{target_date}_exported_papers.json"
    html_file = output_dir / f"{target_date}_report.html"
    markdown_file = output_dir / f"{target_date}_report.md"

    return output_file, selected_paper_file, html_file, markdown_file


def retrieve_papers(
    source: str, target_date: datetime.date
) -> dict[str, list[dict[str, Any]]]:
    """Retrieve papers from the specified source.

    Args:
        source: Source to retrieve from ('arxiv' or 'cool_paper').
        target_date: Date to retrieve papers for.

    Returns:
        Dictionary mapping categories to lists of paper data.
    """
    if source == "arxiv":
        result = retrieve_paper.from_arxiv(
            categories=config.categories, date_day=target_date
        )
    else:
        result = retrieve_paper.from_cool_paper(
            categories=config.categories, date_day=target_date
        )

    total_papers = sum(len(papers) for papers in result.values())
    logger.info(f"Retrieved a total of {total_papers} papers")
    return result


def process_papers(
    papers: dict[str, list[dict[str, Any]]],
    target_date: datetime.date,
    output_file: Path,
    model_name: str,
) -> dict[str, list[dict[str, Any]]]:
    """Process papers by removing duplicates and adding summaries.

    Args:
        papers: Raw papers data.
        target_date: Target date for processing.
        output_file: Path to save processed data.
        model_name: Model name for summarization.

    Returns:
        Processed papers with summaries.
    """
    # Remove duplicates
    processed_papers = postprocess.remove_duplicates_by_id(papers)
    processed_papers = postprocess.remove_by_previous_day(
        processed_papers, target_date, str(output_file)
    )

    new_papers = sum(len(papers) for papers in processed_papers.values())
    logger.info(f"Final count of new papers: {new_papers}")

    # Save intermediate results
    utils.export_to_json(processed_papers, str(output_file))

    # Add summaries
    final_papers = summarize.add_paper_summaries(
        processed_papers, model_name=model_name
    )

    # Save final results
    utils.export_to_json(final_papers, str(output_file))
    logger.info(f"Results saved to {output_file}")

    return final_papers


def generate_reports(
    papers: dict[str, list[dict[str, Any]]], html_file: Path, markdown_file: Path
) -> None:
    """Generate HTML and Markdown reports from processed papers.

    Args:
        papers: Processed papers data.
        html_file: Path for HTML report.
        markdown_file: Path for Markdown report.
    """
    # Flatten papers into a single list
    all_papers = [paper for papers_list in papers.values() for paper in papers_list]

    # Generate HTML report
    html_report.generate(all_papers, str(html_file))
    logger.info(f"HTML report generated at {html_file}")

    # Generate Markdown report
    markdown_report.generate(all_papers, str(markdown_file))
    logger.info(f"Markdown report generated at {markdown_file}")


def load_papers_from_files(
    output_file: str,
    selected_paper_file: str,
    model_name: str,
    regenerate_summaries: bool = False,
) -> list[dict[str, Any]]:
    """Load and process papers from existing files.

    Args:
        output_file: Path to the main papers JSON file.
        selected_paper_file: Path to the selected papers JSON file.
        model_name: Model name for summarization if needed.
        regenerate_summaries: Whether to regenerate paper summaries.

    Returns:
        List of processed paper dictionaries.
    """
    if Path(selected_paper_file).exists():
        logger.info(f"Loading selected papers from {selected_paper_file}")
        selected_papers = utils.load_json(selected_paper_file)
        selected_ids = {paper["pdf_url"] for paper in selected_papers}

        # Load and filter papers
        retrieved_papers = utils.load_json(output_file)
        return [
            paper
            for papers in retrieved_papers.values()
            for paper in papers
            if paper["pdf_url"] in selected_ids
        ]

    logger.info(f"Loading all papers from {output_file}")
    data = utils.load_json(output_file)

    if regenerate_summaries:
        data = summarize.add_paper_summaries(data, model_name=model_name)
        utils.export_to_json(data, output_file)
        logger.info(f"Regenerated summaries and saved to {output_file}")

    return [paper for papers in data.values() for paper in papers]


def process_existing_data(
    output_file: str,
    selected_paper_file: str,
    html_file: str,
    markdown_file: str,
    args: argparse.Namespace,
) -> None:
    """Process existing data files instead of retrieving new papers.

    Args:
        output_file: Path to the main papers JSON file.
        selected_paper_file: Path to the selected papers JSON file.
        html_file: Path to generate the HTML report.
        markdown_file: Path to generate the markdown report.
        args: Command line arguments.
    """
    all_papers = load_papers_from_files(
        output_file, selected_paper_file, args.model, args.resummarize
    )

    # Generate reports if requested or if they don't exist
    if args.html or not Path(html_file).exists():
        html_report.generate(all_papers, html_file)
        logger.info(f"HTML report generated at {html_file}")

    if args.markdown or not Path(markdown_file).exists():
        markdown_report.generate(all_papers, markdown_file)
        logger.info(f"Markdown report generated at {markdown_file}")


def main() -> None:
    """Main function to retrieve and process arXiv papers.

    Retrieves papers from the specified date, removes duplicates, generates summaries,
    and creates HTML and Markdown reports.
    """
    args = parse_args()
    target_date = (
        datetime.date.fromisoformat(args.date) if args.date else datetime.date.today()
    )

    logger.info(f"Collecting papers from {target_date}")

    # Set up output directories
    output_file, selected_paper_file, html_file, markdown_file = (
        setup_output_directories(args.output_path, target_date)
    )

    # Check if we can use existing data
    if output_file.exists() and not args.retrieve:
        logger.info("Using existing data")
        process_existing_data(
            str(output_file),
            str(selected_paper_file),
            str(html_file),
            str(markdown_file),
            args,
        )
        return

    # Retrieve and process papers
    papers = retrieve_papers(args.source, target_date)
    processed_papers = process_papers(papers, target_date, output_file, args.model)

    # Generate reports
    generate_reports(processed_papers, html_file, markdown_file)


if __name__ == "__main__":
    main()
