from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timezone
from typing import List

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from tools.db_tool import get_due_messages, mark_processing, mark_sent, mark_failed, mark_retry
from tools.telegram_tool import send_telegram_message
from schemas.models import ScheduledMessage

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)
logger = logging.getLogger("SchedulerAgent")

class SchedulerAgent:
    """Agent responsible for scheduling and sending messages via Telegram."""

    def __init__(self, check_interval: int = 60):
        """
        Initialize the SchedulerAgent.
        
        Args:
            check_interval: Interval in seconds to check for due messages.
        """
        self.scheduler = AsyncIOScheduler()
        self.check_interval = check_interval
        self.max_retries = 2

    async def process_due_messages(self) -> None:
        """Check for due messages and attempt to send them."""
        now = datetime.now(timezone.utc)
        due_messages: List[ScheduledMessage] = get_due_messages(now)
        
        if not due_messages:
            return

        logger.info(f"[Backend] Found {len(due_messages)} messages due for sending.")

        for msg in due_messages:
            await self._send_message_task(msg)

    async def _send_message_task(self, msg: ScheduledMessage) -> None:
        """Task to handle the sending of a single message."""
        try:
            mark_processing(msg.id)
            logger.info(f"[Backend] Attempting to send message {msg.id} to {msg.target}")
            
            result = await send_telegram_message(msg.target, msg.message)
            
            if result["success"]:
                mark_sent(msg.id)
                logger.info(f"[Backend] Successfully sent message {msg.id} to {msg.target}")
            else:
                error_msg = result.get("error") or "Unknown error"
                await self._handle_failure(msg, error_msg)
                
        except Exception as e:
            logger.exception(f"[Backend] Unexpected error processing message {msg.id}: {e}")
            await self._handle_failure(msg, str(e))

    async def _handle_failure(self, msg: ScheduledMessage, error: str) -> None:
        """Handle failure by either scheduling a retry or marking as failed."""
        if msg.retry_count < self.max_retries:
            mark_retry(msg.id, error)
            logger.warning(f"[Backend] Message {msg.id} failed. Retry {msg.retry_count + 1}/{self.max_retries}. Error: {error}")
        else:
            mark_failed(msg.id, f"Max retries reached. Last error: {error}")
            logger.error(f"[Backend] Message {msg.id} failed permanently after {self.max_retries} retries. Error: {error}")

    def start(self) -> None:
        """Start the scheduler."""
        self.scheduler.add_job(self.process_due_messages, 'interval', seconds=self.check_interval)
        self.scheduler.start()
        logger.info(f"[Backend] Scheduler started. Checking every {self.check_interval} seconds.")

    def shutdown(self) -> None:
        """Shutdown the scheduler."""
        self.scheduler.shutdown()
        logger.info("[Backend] Scheduler shut down.")
