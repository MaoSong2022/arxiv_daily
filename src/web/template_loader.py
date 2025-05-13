from typing import Dict, Optional
import os
from functools import lru_cache


@lru_cache(maxsize=10)
def load_template(template_path: str) -> str:
    """
    Load an HTML template from a file with caching.

    Args:
        template_path: Path to the template file

    Returns:
        String containing the template content

    Raises:
        FileNotFoundError: If the template file doesn't exist
    """
    with open(template_path, "r", encoding="utf-8") as f:
        return f.read()


def get_template(template_name: str) -> str:
    """
    Get a template by name from the templates directory.

    Args:
        template_name: Name of the template file

    Returns:
        String containing the template content
    """
    base_dir = os.path.dirname(os.path.abspath(__file__))
    template_path = os.path.join(base_dir, "templates", template_name)
    return load_template(template_path)
