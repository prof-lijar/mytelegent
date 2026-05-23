from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional

# Setup log directories
LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

ACTIVITY_LOG = LOG_DIR / "activity.log"
ERROR_LOG = LOG_DIR / "errors.log"

class AppLogger:
    \"\"\"Custom logger to handle activity and error logs separately.\"\"\"
    
    def __init__(self, name: str = \"tiny-jarvis\") -> None:
        self.name = name
        self._activity_logger = self._setup_logger(\"activity\", ACTIVITY_LOG)
        self._error_logger = self._setup_logger(\"error\", ERROR_LOG)

    def _setup_logger(self, name: str, log_file: Path) -> logging.Logger:
        logger = logging.getLogger(f\"{self.name}.{name}\")
        logger.setLevel(logging.INFO)
        
        # Avoid duplicate handlers if initialized multiple times
        if not logger.handlers:
            handler = logging.FileHandler(log_file, encoding=\"utf-8\")
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger

    def info(self, message: str) -> None:
        \"\"\"Log a general activity message.\"\"\"
        self._activity_logger.info(message)

    def error(self, message: str, exc_info: Optional[bool] = False) -> None:
        \"\"\"Log an error message.\"\"\"
        self._error_logger.error(message, exc_info=exc_info)

    def warning(self, message: str) -> None:
        \"\"\"Log a warning message.\"\"\"
        self._activity_logger.warning(message)

_loggers_cache = {}

def get_logger(name: str) -> AppLogger:
    \"\"\"Get or create a logger instance for the given name.\"\"\"
    if name not in _loggers_cache:
        _loggers_cache[name] = AppLogger(name)
    return _loggers_cache[name]

# Default singleton for general use
logger = get_logger(\"main\")
