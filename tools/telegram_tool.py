from __future__ import annotations

import asyncio
import random
import logging
from typing import Dict, Any, Optional

from telethon import TelegramClient, errors
from tools.config import Config

# Setup logging
logger = logging.getLogger(__name__)

class TelegramTool:
    """Tool for interacting with Telegram via Telethon."""

    def __init__(self) -> None:
        """Initialize the TelegramTool with config values."""
        # Note: validation is now done in get_client to avoid import-time errors in tests
        self.api_id = Config.TELEGRAM_API_ID
        self.api_hash = Config.TELEGRAM_API_HASH
        self.session_path = "database/telegram_session"
        self.client: Optional[TelegramClient] = None

    async def get_client(self) -> TelegramClient:
        """Get or create the TelegramClient instance."""
        Config.validate_telegram_config()
        if self.client is None:
            self.client = TelegramClient(
                self.session_path, 
                int(self.api_id), 
                self.api_hash
            )
            await self.client.start()
        return self.client

    async def is_authorized(self) -> bool:
        """Check if the Telegram client is authorized."""
        try:
            client = await self.get_client()
            await client.get_me()
            return True
        except Exception as e:
            logger.error(f"[Backend] Authorization check failed: {e}")
            return False

    async def send_message(self, target: str, message: str) -> Dict[str, Any]:
        """
        Send a message to a target (username or phone).
        Includes a random delay to avoid spam filters.
        """
        try:
            # Safety Rule: Random delay 2-5 seconds
            delay = random.uniform(2, 5)
            await asyncio.sleep(delay)

            client = await self.get_client()
            await client.send_message(target, message)
            
            return {"success": True, "target": target, "error": None}
        except errors.FloodWaitError as e:
            logger.error(f"[Backend] FloodWaitError: {e.seconds} seconds")
            return {"success": False, "target": target, "error": f"FloodWait: {e.seconds}s"}
        except Exception as e:
            # Catch all other exceptions (including Telethon specific ones)
            logger.error(f"[Backend] Error sending to {target}: {e}")
            return {"success": False, "target": target, "error": str(e)}

# Singleton instance
_tool_instance: Optional[TelegramTool] = None

def get_telegram_tool() -> TelegramTool:
    """Get the singleton instance of TelegramTool."""
    global _tool_instance
    if _tool_instance is None:
        _tool_instance = TelegramTool()
    return _tool_instance

async def send_telegram_message(target: str, message: str) -> Dict[str, Any]:
    """
    Async wrapper to send a telegram message.
    As per Guide: No internal retry logic here; handled by scheduler.
    """
    tool = get_telegram_tool()
    return await tool.send_message(target, message)

if __name__ == "__main__":
    # Simple manual test block
    import asyncio
    async def test():
        tool = get_telegram_tool()
        print(f"Authorized: {await tool.is_authorized()}")
    
    asyncio.run(test())
