from typing import Dict, List, Any
from loguru import logger
import os
from .template_loader import get_template


boring_sections = ["others"]


def generate_html_report(data: List[Dict[str, Any]], output_path: str) -> None:
    """
    Generate an HTML report that categorizes papers based on predefined classifiers.

    Args:
        data: List of paper data dictionaries
        output_path: Path where the HTML file will be saved

    Returns:
        None
    """
    logger.info("Generating HTML report...")

    # Initialize sections with empty lists
    sections: Dict[str, List[Dict[str, Any]]] = {}

    # Categorize papers
    for paper in data:
        # Check if paper has pre-assigned classifiers
        classifiers = paper.get("classifiers", ["Unknown"])
        if not classifiers:
            classifiers = ["Unknown"]

        # Add paper to all its classifier categories
        for classifier in classifiers:
            if classifier.lower() not in sections:
                sections[classifier.lower()] = []
            sections[classifier.lower()].append(paper)

    # Create output directory if it doesn't exist
    output_dir = os.path.dirname(output_path)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Create assets directory
    css_path = os.path.join("assets", "styles.css")
    js_path = os.path.join("assets", "scripts.js")

    # Generate HTML content
    html_content = get_html_header(css_path, js_path) + get_html_body(sections)

    # Write to file
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    logger.info(f"HTML report generated at {output_path}")


def get_html_header(css_path: str, js_path: str) -> str:
    """
    Generate the HTML header with embedded CSS and JS content for improved portability.

    Args:
        css_path: Path to the CSS file
        js_path: Path to the JavaScript file

    Returns:
        String containing HTML header content with embedded CSS and JS
    """
    # Read CSS and JS content from files
    css_content = ""
    if os.path.exists(css_path):
        with open(css_path, "r", encoding="utf-8") as css_file:
            css_content = css_file.read()

    js_content = ""
    if os.path.exists(js_path):
        with open(js_path, "r", encoding="utf-8") as js_file:
            js_content = js_file.read()

    html_header = "<html><head>"
    html_header += "<meta charset='UTF-8'>"
    html_header += (
        "<meta name='viewport' content='width=device-width, initial-scale=1.0'>"
    )
    html_header += "<title>ArXiv Papers Report</title>"
    html_header += f"<style>\n{css_content}\n</style>"
    html_header += f"<script>\n{js_content}\n</script>"
    html_header += "</head><body>\n"

    return html_header


def get_html_body(sections: Dict[str, List[Dict[str, Any]]]) -> str:
    """
    Generate the HTML body content with paper sections.

    Args:
        sections: Dictionary mapping classifiers to lists of paper data

    Returns:
        String containing HTML body content
    """
    # Load the main layout template
    template = get_template("main_layout_template.html")

    # Generate sidebar navigation items
    sidebar_items = ""

    # Filter out empty sections and "Others"
    valid_sections = {
        section: papers
        for section, papers in sections.items()
        if papers and section not in boring_sections
    }

    for section, papers in valid_sections.items():
        section_id = section.lower().replace(" ", "-")
        paper_count = len(papers)
        sidebar_items += f'<li><a class="sidebar-link" data-section="{section_id}" '
        sidebar_items += (
            f"onclick=\"scrollToSection('{section_id}')\"><span>{section}</span>"
        )
        sidebar_items += f'<span class="paper-count">{paper_count}</span></a></li>\n'

    # Generate main content sections
    content_sections = ""

    for section, papers in sections.items():
        if (
            not papers or section in boring_sections
        ):  # Skip empty sections and boring sections
            continue

        # Create section ID for navigation
        section_id = section.lower().replace(" ", "-")

        # Generate paper cards for this section
        paper_cards = ""
        for paper in papers:
            paper_cards += generate_paper_card(paper)

        # Use the section template
        section_template = get_template("section_template.html")
        content_sections += section_template.format(
            section_id=section_id,
            section_name=section,
            paper_count=len(papers),
            paper_cards=paper_cards,
        )

    # Add export buttons
    export_buttons = """
<div class="export-container">
  <button class="export-button" onclick="exportSelectedPapers()">
    <svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path d="M8 12L3 7L4.4 5.55L7 8.15V0H9V8.15L11.6 5.55L13 7L8 12Z" fill="white"/>
      <path d="M14 14H2V7H0V14C0 15.1 0.9 16 2 16H14C15.1 16 16 15.1 16 14V7H14V14Z" fill="white"/>
    </svg>
    Export as JSON
  </button>
  <button class="export-button markdown-export-button" onclick="exportSelectedPapersToMarkdown()">
    <svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path d="M14 1H2C0.9 1 0 1.9 0 3V13C0 14.1 0.9 15 2 15H14C15.1 15 16 14.1 16 13V3C16 1.9 15.1 1 14 1ZM14 13H2V3H14V13Z" fill="white"/>
      <path d="M2 7H4V11H6V7H8L5 4L2 7Z" fill="white"/>
      <path d="M8 9H10V11H12V9H14L11 6L8 9Z" fill="white"/>
    </svg>
    Export as Markdown
  </button>
</div>
"""

    # Fill in the main template
    html = template.format(
        sidebar_items=sidebar_items,
        content_sections=content_sections,
        export_buttons=export_buttons,
    )

    return html


def generate_paper_card(paper: Dict[str, Any]) -> str:
    """
    Generate HTML for a single paper card.

    Args:
        paper: Dictionary containing paper data

    Returns:
        String containing HTML for the paper card
    """
    # Load the template
    template = get_template("paper_card_template.html")

    # Extract paper data
    title = paper.get("title", "No Title")
    pdf_url = paper.get("pdf_url", "")
    keywords = paper.get("keywords", [])
    tldr = paper.get("tldr", "")
    authors = paper.get("authors", [])
    abstract = paper.get("abstract", "")
    paper_id = paper.get("id", "")
    comments = paper.get("comments", "")

    # Extract date information
    published = paper.get("published", None)
    updated = paper.get("updated", None)

    # Generate authors section
    authors_section = ""
    if authors:
        authors_section = f"""
    <div class="authors">
      <span class="metadata-label">Authors:</span> {", ".join(authors)}
    </div>
"""

    # Generate date section
    date_section = ""
    if published or updated:
        date_section = '<div class="paper-dates">'

        if published:
            # Format the date if it's a datetime object, otherwise use as is
            published_str = (
                published.strftime("%Y-%m-%d %H:%M:%S")
                if hasattr(published, "strftime")
                else published
            )
            date_section += f'<div class="date-item"><span class="metadata-label">Published:</span> <span class="date-value">{published_str}</span></div>'

        if updated and updated != published:
            # Format the date if it's a datetime object, otherwise use as is
            updated_str = (
                updated.strftime("%Y-%m-%d %H:%M:%S")
                if hasattr(updated, "strftime")
                else updated
            )
            date_section += f'<div class="date-item"><span class="metadata-label">Updated:</span> <span class="date-value">{updated_str}</span></div>'

        date_section += "</div>"

    # Generate keywords inputs
    keywords_inputs = ""
    if keywords:
        keywords_inputs = "\n".join(
            [
                f'      <input type="text" class="keyword-input" value="{keyword.strip()}">'
                for keyword in keywords
            ]
        )
    else:
        keywords_inputs = (
            '      <input type="text" class="keyword-input" placeholder="Add keyword">'
        )

    # Generate abstract section
    abstract_section = ""
    if abstract:
        abstract_section = f"""
  <div class="abstract-container">
    <button class="toggle-abstract" onclick="toggleAbstract(this)">Show Abstract</button>
    <div class="abstract" style="display:none;">
      <p>{abstract}</p>
    </div>
  </div>
"""

    # Fill in the template
    html = template.format(
        paper_id=paper_id,
        title=title,
        pdf_url=pdf_url,
        authors_section=authors_section,
        date_section=date_section,
        keywords_inputs=keywords_inputs,
        comments=comments,
        tldr=tldr,
        abstract_section=abstract_section,
    )

    return html
