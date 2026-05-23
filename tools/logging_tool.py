from __future__ import annotations

import logging
from pathlib import Path

# Ensure logs directory exists
LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

ACTIVITY_LOG = LOG_DIR / "activity.log"
ERROR_LOG = LOG_DIR / "errors.log"

class CustomLogger:
    """Dual handler logger for activity and errors."""
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        
        # Avoid duplicate handlers if logger is retrieved multiple times
        if not self.logger.handlers:
            # Activity handler (INFO and above)
            activity_handler = logging.FileHandler(ACTIVITY_LOG)
            activity_handler.setLevel(logging.INFO)
            activity_fmt = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            activity_handler.setFormatter(activity_fmt)
            
            # Error handler (ERROR and above)
            error_handler = logging.FileHandler(ERROR_LOG)
            error_handler.setLevel(logging.ERROR)
            error_fmt = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            error_handler.setFormatter(error_fmt)
            
            self.logger.addHandler(activity_handler)
            self.logger.addHandler(error_handler)

    def info(self, msg: str) -> None:
        """Log general application flow."""
        self.logger.info(msg)

    def error(self, msg: str, exc_info: bool = False) -> None:
        """Log errors and optionally tracebacks."""
        self.logger.error(msg, exc_info=exc_info)

    def debug(self, msg: str) -> None:
        """Log debug information."""
        self.logger.debug(msg)

def get_logger(name: str) -> CustomLogger:
    """Get a logger instance for the given name."""
    return CustomLogger(name)
