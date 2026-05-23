from __future__ import annotations

import logging
from pathlib import Path
from logging.handlers import RotatingFileHandler

# Configuration
LOG_DIR = Path("logs")
ACTIVITY_LOG = LOG_DIR / "activity.log"
ERROR_LOG = LOG_DIR / "errors.log"

def setup_logging() -> None:
    \"\"\"Set up dual logging handlers for activity and errors.\"\"\"
    LOG_DIR.mkdir(exist_ok=True)

    # Create logger
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # Clear existing handlers to avoid duplicates
    if logger.hasHandlers():
        logger.handlers.clear()

    # Formatter
    formatter = logging.Formatter(
        '[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s'
    )

    # Activity Log Handler (INFO and above)
    activity_handler = RotatingFileHandler(
        ACTIVITY_LOG, maxBytes=5*1024*1024, backupCount=5
    )
    activity_handler.setLevel(logging.INFO)
    activity_handler.setFormatter(formatter)

    # Error Log Handler (ERROR and above)
    error_handler = RotatingFileHandler(
        ERROR_LOG, maxBytes=5*1024*1024, backupCount=5
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)

    logger.addHandler(activity_handler)
    logger.addHandler(error_handler)

def get_logger(name: str) -> logging.Logger:
    \"\"\"Get a logger instance with the specified name.\"\"\"
    return logging.getLogger(name)
