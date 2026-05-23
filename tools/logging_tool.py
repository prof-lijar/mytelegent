from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional

# Setup paths
LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

ACTIVITY_LOG = LOG_DIR / "activity.log"
ERROR_LOG = LOG_DIR / "errors.log"

def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance configured to write to activity.log and errors.log.
    
    Args:
        name: Name of the logger (usually __name__).
    """
    logger = logging.getLogger(name)
    
    # Avoid adding handlers multiple times if get_logger is called again for the same name
    if logger.hasHandlers():
        return logger

    logger.setLevel(logging.DEBUG)
    
    # Formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Activity handler (INFO and above)
    activity_handler = logging.FileHandler(ACTIVITY_LOG, encoding='utf-8')
    activity_handler.setLevel(logging.INFO)
    activity_handler.setFormatter(formatter)
    
    # Error handler (ERROR and above)
    error_handler = logging.FileHandler(ERROR_LOG, encoding='utf-8')
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)

    logger.addHandler(activity_handler)
    logger.addHandler(error_handler)
    
    return logger
