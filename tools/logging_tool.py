from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional

# Create logs directory if it doesn't exist
LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

ACTIVITY_LOG = LOG_DIR / "activity.log"
ERROR_LOG = LOG_DIR / "errors.log"

class DualLogger:
    """Logger that separates activity and error logs."""
    
    def __init__(self, name: str = "tiny-jarvis"):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        
        if not self.logger.handlers:
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )

            # Activity Handler (INFO and below)
            activity_handler = logging.FileHandler(ACTIVITY_LOG)
            activity_handler.setLevel(logging.INFO)
            activity_handler.setFormatter(formatter)
            activity_handler.addFilter(lambda record: record.levelno <= logging.INFO)

            # Error Handler (WARNING and above)
            error_handler = logging.FileHandler(ERROR_LOG)
            error_handler.setLevel(logging.WARNING)
            error_handler.setFormatter(formatter)

            self.logger.addHandler(activity_handler)
            self.logger.addHandler(error_handler)

    def info(self, message: str) -> None:
        """Log a general activity event."""
        self.logger.info(message)

    def error(self, message: str, exc_info: Optional[bool] = False) -> None:
        """Log an error event."""
        self.logger.error(message, exc_info=exc_info)

    def warning(self, message: str) -> None:
        """Log a warning event."""
        self.logger.warning(message)

    def debug(self, message: str) -> None:
        """Log a debug event."""
        self.logger.debug(message)

def get_logger(name: str) -> DualLogger:
    """Return a DualLogger instance for the given name."""
    return DualLogger(name)

# Singleton instance for general use
logger = DualLogger()
