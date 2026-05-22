from dotenv import load_dotenv
from pydantic import BaseModel
import os

class Config(BaseModel):
    LOCAL_LLM_BASE_URL: str = "http://localhost:11434/v1"
    LOCAL_LLM_MODEL: str = "gemma4"
    LOCAL_LLM_API_KEY: str = "ollama"
    TIMEZONE: str = "Asia/Seoul"
    SQLITE_DB_PATH: str = "database/messages.db"

    @classmethod
def get_config(cls) -> 'Config':
        load_dotenv()
        return cls(
            LOCAL_LLM_BASE_URL=os.getenv('LOCAL_LLM_BASE_URL', cls.LOCAL_LLM_BASE_URL),
            LOCAL_LLM_MODEL=os.getenv('LOCAL_LLM_MODEL', cls.LOCAL_LLM_MODEL),
            LOCAL_LLM_API_KEY=os.getenv('LOCAL_LLM_API_KEY', cls.LOCAL_LLM_API_KEY),
            TIMEZONE=os.getenv('TIMEZONE', cls.TIMEZONE),
            SQLITE_DB_PATH=os.getenv('SQLITE_DB_PATH', cls.SQLITE_DB_PATH)
        )