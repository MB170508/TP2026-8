"""Production logging setup for IT Toolbox.

Provides file-based (DEBUG) and console (WARNING+) logging.
Log directory: ~/.ittoolbox/logs/toolbox.log
"""

import logging
import logging.handlers
from pathlib import Path

# Configuration
LOG_DIR = Path.home() / ".ittoolbox" / "logs"
LOG_FILE = LOG_DIR / "toolbox.log"

# Format: timestamp | level | module:function:line | message
LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s:%(funcName)s:%(lineno)d | %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def init_logging():
    """Initialize logging infrastructure.

    Creates ~/.ittoolbox/logs/ directory and configures:
    - File handler: DEBUG level (detailed)
    - Console handler: WARNING level (user-facing)
    """
    # Create log directory
    LOG_DIR.mkdir(parents=True, exist_ok=True)

    # Get root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)

    # Remove existing handlers to avoid duplicates
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # File handler (DEBUG level, all messages)
    file_handler = logging.FileHandler(LOG_FILE)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT))
    root_logger.addHandler(file_handler)

    # Console handler (WARNING+ level, important messages only)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.WARNING)
    console_handler.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))
    root_logger.addHandler(console_handler)


def get_logger(name):
    """Get a logger instance for a module.

    Args:
        name: Module name, typically __name__

    Returns:
        logging.Logger instance
    """
    return logging.getLogger(name)
