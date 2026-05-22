from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

load_dotenv()

class Config:
    """Configuration loader for tiny-jarvis."""
    
    # LLM Settings
    LOCAL_LLM_BASE_URL: str = os.getenv("LOCAL_LLM_BASE_URL", "http://localhost:11434/v1")
    LOCAL_LLM_MODEL: str = os.getenv("LOCAL_LLM_MODEL", "gemma4")
    LOCAL_LLM_API_KEY: str = os.getenv("LOCAL_LLM_API_KEY", "ollama")

    # Telegram Settings
    TELEGRAM_API_ID: Optional[str] = os.getenv("TELEGRAM_API_ID")
    TELEGRAM_API_HASH: Optional[str] = os.getenv("TELEGRAM_API_HASH")

    # Database Settings
    DB_PATH: str = os.getenv("SQLITE_DB_PATH", "database/messages.db")
    
    # General Settings
    TIMEZONE: str = os.getenv("TIMEZONE", "Asia/Seoul")

    @classmethod
    def validate_telegram_config(cls) -> None:
        """Validate that required Telegram environment variables are set."""
        if not cls.TELEGRAM_API_ID or not cls.TELEGRAM_API_HASH:
            raise EnvironmentError(
                "TELEGRAM_API_ID and TELEGRAM_API_HASH must be set in the environment."
            )

    @classmethod
    def ensure_db_dir(cls) -> None:
        """Ensure the directory for the SQLite database exists."""
        db_path = Path(cls.DB_PATH)
        db_path.parent.mkdir(parents=True, exist_ok=True)
