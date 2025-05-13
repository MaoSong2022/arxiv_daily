import os
import sys
import json
import datetime
import argparse
from typing import List, Dict, Any, Union

from loguru import logger
from dotenv import load_dotenv

from src.utils import export_to_json
from src.data.retrieve_paper import query_arxiv_papers
from src.web.generate_html import generate_html_report
from src.generation.generate_markdown_report import generate_markdown_report
from src.data.summarize import add_paper_summaries
from src.data.postprocess_paper import remove_duplicates_by_id
from src.config import config

# Load environment variables
load_dotenv()

os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
os.environ["API_BASE_URL"] = os.getenv("API_BASE_URL")

# Configure logging
logger.remove()
logger.add("daily.log", mode="w")
logger.add(sys.stdout, level="INFO")


def load_json(
    file_path: str,
) -> Union[List[Dict[str, Any]], Dict[str, List[Dict[str, Any]]]]:
    """
    Load JSON data from a file.

    Args:
        file_path: Path to the JSON file

    Returns:
        The parsed JSON data as a list of dictionaries or a dictionary of lists
    """
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def parse_args() -> argparse.Namespace:
    """
    Parse command line arguments.
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
    return parser.parse_args()


def main() -> None:
    """
    Main function to retrieve yesterday's arXiv papers in specified categories.

    Command line arguments:
        --retrieve: Retrieve papers again even if output file exists
        --html: Regenerate HTML report
        --markdown: Regenerate markdown report
        --resummarize: Regenerate summaries for papers
        --date: Date to collect papers for (YYYY-MM-DD format). Defaults to today if not provided.
        --model: Model name to use for generating summaries (default: qwen2.5:32b)
    """
    # Parse command line arguments
    args = parse_args()

    # Ensure output directory exists
    os.makedirs(args.output_path, exist_ok=True)

    # Use provided date or default to today
    if args.date:
        target_date = datetime.date.fromisoformat(args.date)
    else:
        target_date = datetime.date.today()

    target_month = target_date.strftime("%Y-%m")

    output_file = f"{args.output_path}/{target_month}/{str(target_date)}.json"
    selected_paper_file = (
        f"{args.output_path}/{target_month}/{str(target_date)}_exported_papers.json"
    )
    html_file = f"{args.output_path}/{target_month}/{str(target_date)}_report.html"
    markdown_file = f"{args.output_path}/{target_month}/{str(target_date)}_report.md"

    logger.info(f"Collecting papers from {str(target_date)}")

    # Check if we can use existing data or need to retrieve new papers
    if os.path.exists(output_file) and not args.retrieve:
        process_existing_data(
            output_file, selected_paper_file, html_file, markdown_file, args
        )
        return

    # Step 1: Retrieve papers from yesterday
    result = query_arxiv_papers(categories=config.categories, date_day=target_date)

    # Count total papers
    total_papers = sum(len(papers) for category, papers in result.items())
    logger.info(f"Retrieved a total of {total_papers} papers")

    # Step 2: Remove duplicates
    final_results = remove_duplicates_by_id(result)
    new_papers = sum(len(papers) for papers in final_results.values())
    logger.info(f"Final count of new papers: {new_papers}")
    export_to_json(final_results, output_file)

    # Step 3: Add TL;DR summaries and keywords to papers
    final_results = add_paper_summaries(final_results, model_name=args.model)

    # Save results to file
    export_to_json(final_results, output_file)
    logger.info(f"Results saved to {output_file}")

    # Flatten the dictionary into a list of papers
    all_papers = []
    for category, papers in final_results.items():
        all_papers.extend(papers)

    # Step 5: Generate HTML report
    generate_html_report(all_papers, html_file)
    logger.info(f"HTML report generated at {html_file}")

    # Step 6: Generate markdown report
    generate_markdown_report(all_papers, markdown_file)
    logger.info(f"Markdown report generated at {markdown_file}")


def process_existing_data(
    output_file: str,
    selected_paper_file: str,
    html_file: str,
    markdown_file: str,
    args: argparse.Namespace,
) -> None:
    """
    Process existing data files instead of retrieving new papers.

    Args:
        output_file: Path to the main papers JSON file
        selected_paper_file: Path to the selected papers JSON file
        html_file: Path to generate the HTML report
        markdown_file: Path to generate the markdown report
        args: Command line arguments
    """
    all_papers = []

    # Check if we have selected papers
    if os.path.exists(selected_paper_file):
        selected_papers = load_json(selected_paper_file)
        selected_ids = [paper["pdf_url"] for paper in selected_papers]

        # Load retrieved papers and filter for selected ones
        retrieved_papers = load_json(output_file)
        for _, papers in retrieved_papers.items():
            for paper in papers:
                if paper["pdf_url"] in selected_ids:
                    all_papers.append(paper)
    else:
        # Load all papers from the output file
        with open(output_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Regenerate summaries if requested
        if args.resummarize:
            data = add_paper_summaries(data, model_name=args.model)
            export_to_json(data, output_file)
            logger.info(f"Regenerated summaries and saved to {output_file}")

        # Collect all papers
        for _, papers in data.items():
            all_papers.extend(papers)

    # Generate reports if requested or if they don't exist
    if args.html or not os.path.exists(html_file):
        generate_html_report(all_papers, html_file)
        logger.info(f"HTML report generated at {html_file}")

    if args.markdown or not os.path.exists(markdown_file):
        generate_markdown_report(all_papers, markdown_file)
        logger.info(f"Markdown report generated at {markdown_file}")


if __name__ == "__main__":
    main()
