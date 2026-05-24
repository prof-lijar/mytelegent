from __future__ import annotations

import asyncio
import random
from typing import Dict, Optional

from telethon import TelegramClient, errors
from tools.config import Config
from tools.logging_tool import get_logger

logger = get_logger("telegram_tool")

async def send_telegram_message(target: str, message: str) -> Dict[str, Optional[str]]:
    """
    Send a message via Telegram using the Telethon client.
    
    Args:
        target: The recipient (phone, username, or name).
        message: The text message to send.
        
    Returns:
        A dictionary indicating success or failure.
    """
    # Requirement: Random delay 2-5 seconds before sending
    delay = random.uniform(2, 5)
    await asyncio.sleep(delay)

    try:
        # Validate required Telegram vars
        Config.validate_telegram_config()
        
        async with TelegramClient(
            'tiny_jarvis_session', 
            Config.TELEGRAM_API_ID, 
            Config.TELEGRAM_API_HASH
        ) as client:
            await client.send_message(target, message)
            
        logger.info(f"Successfully sent message to {target}")
        return {"success": True, "target": target, "error": None}

    except errors.UserIdInvalidError:
        err = f"Invalid user ID or username: {target}"
        logger.error(err)
        return {"success": False, "target": target, "error": err}
    except errors.PhoneCodeInvalidError:
        err = "Invalid phone code provided for Telegram authentication"
        logger.error(err)
        return {"success": False, "target": target, "error": err}
    except Exception as e:
        err = f"Unexpected error sending message to {target}: {str(e)}"
        logger.error(err, exc_info=True)
        return {"success": False, "target": target, "error": err}

if __name__ == "__main__":
    # Manual test block
    import asyncio
    
    async def test_send():
        # Replace with a real target for testing if needed
        res = await send_telegram_message("@me", "Test message from tiny-jarvis")
        print(res)

    asyncio.run(test_send())
