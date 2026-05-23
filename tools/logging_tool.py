from __future__ import annotations

import logging
from pathlib import Path
from typing import Dict

# Ensure logs directory exists
LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

ACTIVITY_LOG = LOG_DIR / "activity.log"
ERROR_LOG = LOG_DIR / "errors.log"

class AppLogger:
    """Custom logger that handles dual logging to activity and error files."""
    
    def __init__(self):
        self._loggers: Dict[str, logging.Logger] = {}
        self._formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # File handlers
        self._activity_handler = logging.FileHandler(ACTIVITY_LOG)
        self._activity_handler.setLevel(logging.INFO)
        self._activity_handler.setFormatter(self._formatter)

        self._error_handler = logging.FileHandler(ERROR_LOG)
        self._error_handler.setLevel(logging.ERROR)
        self._error_handler.setFormatter(self._formatter)

    def get_logger(self, name: str) -> logging.Logger:
        """Get or create a named logger with configured handlers."""
        if name in self._loggers:
            return self._loggers[name]

        logger = logging.getLogger(name)
        logger.setLevel(logging.DEBUG)
        
        # Clear existing handlers to avoid duplicates
        if logger.hasHandlers():
            logger.handlers.clear()

        logger.addHandler(self._activity_handler)
        logger.addHandler(self._error_handler)
        
        self._loggers[name] = logger
        return logger

# Singleton instance
_app_logger_instance = AppLogger()

def get_logger(name: str) -> logging.Logger:
    """Utility function to get a logger instance by name."""
    return _app_logger_instance.get_logger(name)
