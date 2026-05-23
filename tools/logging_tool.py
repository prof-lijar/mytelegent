from __future__ import annotations

import logging
from pathlib import Path

# Ensure logs directory exists
LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

ACTIVITY_LOG = LOG_DIR / "activity.log"
ERROR_LOG = LOG_DIR / "errors.log"

class CustomFormatter(logging.Formatter):
    \"\"\"Custom formatter to avoid logging sensitive data.\"\"\"
    SENSITIVE_KEYS = ["TELEGRAM_API_HASH", "api_hash", "api_key"]

    def format(self, record: logging.LogRecord) -> str:
        msg = super().format(record)
        for key in self.SENSITIVE_KEYS:
            if key in msg:
                msg = msg.replace(key, "[REDACTED]")
        return msg

def setup_logging() -> None:
    \"\"\"Initialize dual logging handlers for activity and errors.\"\"\"
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # Clear existing handlers to avoid duplicates
    if logger.hasHandlers():
        logger.handlers.clear()

    formatter = CustomFormatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    # Activity Handler (INFO and above)
    activity_handler = logging.FileHandler(ACTIVITY_LOG)
    activity_handler.setLevel(logging.INFO)
    activity_handler.setFormatter(formatter)

    # Error Handler (ERROR and above)
    error_handler = logging.FileHandler(ERROR_LOG)
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)

    logger.addHandler(activity_handler)
    logger.addHandler(error_handler)

def get_logger(name: str) -> logging.Logger:
    \"\"\"Get a logger instance with the specified name.\"\"\"
    return logging.getLogger(name)

if __name__ == "__main__":
    # Simple test for the logging tool
    setup_logging()
    log = get_logger("test_logger")
    log.info("This is an activity log entry.")
    log.error("This is an error log entry.")
    log.info("Testing redaction: TELEGRAM_API_HASH=12345")
    print(f"Logs written to {ACTIVITY_LOG} and {ERROR_LOG}")
