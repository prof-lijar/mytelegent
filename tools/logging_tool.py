from __future__ import annotations

import logging
from pathlib import Path

# Create logs directory if it doesn't exist
LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

ACTIVITY_LOG = LOG_DIR / "activity.log"
ERROR_LOG = LOG_DIR / "errors.log"

class LevelFilter(logging.Filter):
    """Filter that allows only logs up to a certain level."""
    def __init__(self, max_level: int):
        super().__init__()
        self.max_level = max_level

    def filter(self, record):
        return record.levelno <= self.max_level

def setup_logging() -> logging.Logger:
    """Initialize the logging system with dual handlers for activity and errors."""
    logger = logging.getLogger("tiny_jarvis")
    logger.setLevel(logging.DEBUG)

    if logger.hasHandlers():
        return logger

    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    )

    # Activity Log: DEBUG, INFO, WARNING
    activity_handler = logging.FileHandler(ACTIVITY_LOG, encoding="utf-8")
    activity_handler.setLevel(logging.DEBUG)
    activity_handler.setFormatter(formatter)
    activity_handler.addFilter(LevelFilter(logging.WARNING))

    # Error Log: ERROR, CRITICAL
    error_handler = logging.FileHandler(ERROR_LOG, encoding="utf-8")
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)

    logger.addHandler(activity_handler)
    logger.addHandler(error_handler)

    return logger

def get_logger(name: str) -> logging.Logger:
    """Get a logger instance with the specified name."""
    # Initialize the root-like logger first
    setup_logging()
    return logging.getLogger(f"tiny_jarvis.{name}")

# Initialize logger instance for use across the app
logger = setup_logging()
