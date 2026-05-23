from __future__ import annotations

import logging
from pathlib import Path

# Ensure logs directory exists
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)

ACTIVITY_LOG = log_dir / "activity.log"
ERROR_LOG = log_dir / "errors.log"

class ActivityHandler(logging.FileHandler):
    def emit(self, record):
        if record.levelno <= logging.INFO:
            super().emit(record)

class ErrorHandler(logging.FileHandler):
    def emit(self, record):
        if record.levelno >= logging.ERROR:
            super().emit(record)

def setup_logger() -> logging.Logger:
    \"\"\"Initialize and return the application logger.\"\"\"
    logger = logging.getLogger("tiny-jarvis")
    logger.setLevel(logging.DEBUG)

    if not logger.handlers:
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )

        # Activity log: INFO and below
        activity_handler = ActivityHandler(ACTIVITY_LOG)
        activity_handler.setLevel(logging.DEBUG)
        activity_handler.setFormatter(formatter)
        logger.addHandler(activity_handler)

        # Error log: ERROR and above
        error_handler = ErrorHandler(ERROR_LOG)
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(formatter)
        logger.addHandler(error_handler)

    return logger

def get_logger(name: str) -> logging.Logger:
    \"\"\"Return a logger with the given name, ensuring it uses the app configuration.\"\"\"
    app_logger = setup_logger()
    # We use the app_logger's handlers for consistency across the project
    logger = logging.getLogger(f"tiny-jarvis.{name}")
    logger.setLevel(app_logger.level)
    
    if not logger.handlers:
        # Inherit handlers from the root-like setup_logger
        for handler in app_logger.handlers:
            logger.addHandler(handler)
            
    return logger

logger = setup_logger()
