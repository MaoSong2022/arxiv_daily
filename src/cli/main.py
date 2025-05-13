import argparse
import logging
import sys
from pathlib import Path
from typing import List, Optional

from src.config.settings import settings
from src.utils.logging import setup_logging

logger = logging.getLogger(__name__)


def parse_args(args: Optional[List[str]] = None) -> argparse.Namespace:
    """Parse command line arguments.

    Args:
        args: Command line arguments (defaults to sys.argv[1:]).

    Returns:
        Parsed arguments.
    """
    parser = argparse.ArgumentParser(description=settings.app_name)

    parser.add_argument("--config", type=Path, help="Path to configuration file")

    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        default=settings.log_level,
        help="Set the logging level",
    )

    # Add subparsers for different commands
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Example command
    process_parser = subparsers.add_parser("process", help="Process data")
    process_parser.add_argument("input", type=Path, help="Input file path")
    process_parser.add_argument("--output", type=Path, help="Output file path")

    return parser.parse_args(args)


def main(args: Optional[List[str]] = None) -> int:
    """Main entry point for the CLI.

    Args:
        args: Command line arguments (defaults to sys.argv[1:]).

    Returns:
        Exit code.
    """
    parsed_args = parse_args(args)

    # Set up logging
    setup_logging(log_level=parsed_args.log_level)

    try:
        if parsed_args.command == "process":
            from ..services.processor import process_file

            process_file(parsed_args.input, parsed_args.output)
        else:
            logger.error("No command specified")
            return 1

        return 0
    except Exception as e:
        logger.exception(f"Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
