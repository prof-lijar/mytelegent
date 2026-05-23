from __future__ import annotations

import asyncio
import logging
import random
from datetime import datetime, timezone
from typing import List

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from tools.db_tool import (
    get_due_messages,
    mark_failed,
    mark_processing,
    mark_sent,
    get_db_connection
)
from tools.telegram_tool import send_telegram_message
from tools.logging_tool import get_logger

logger = get_logger("scheduler_agent")

class SchedulerAgent:
    """Agent responsible for scheduling and sending Telegram messages."""

    def __init__(self, check_interval: int = 60) -> None:
        """Initialize the scheduler agent."""
        self.scheduler = AsyncIOScheduler()
        self.check_interval = check_interval
        self.max_retries = 2

    async def process_due_messages(self) -> None:
        """Check for due messages and trigger sending."""
        now = datetime.now(timezone.utc)
        due_messages = get_due_messages(now)
        
        if not due_messages:
            return

        logger.info(f"[Backend] Found {len(due_messages)} due messages to process.")

        # Process sequentially to avoid bulk sending and respect random delays
        for msg in due_messages:
            await self._handle_send(msg)

    async def _handle_send(self, msg) -> None:
        """Handle the end-to-end process of sending a single message."""
        try:
            # 1. Mark as processing to avoid double-send
            mark_processing(msg.id)
            
            logger.info(f"[Backend] Attempting to send message {msg.id} to {msg.target} (Retry: {msg.retry_count}).")
            
            # 2. Send via Telegram tool
            result = await send_telegram_message(msg.target, msg.message)
            
            if result["success"]:
                mark_sent(msg.id)
                logger.info(f"[Backend] Successfully sent message {msg.id} to {msg.target}.")
            else:
                error = result.get("error", "Unknown telegram error")
                await self._handle_failure(msg, error)
                
        except Exception as e:
            logger.error(f"[Backend] Unexpected error processing message {msg.id}: {e}")
            await self._handle_failure(msg, str(e))

    async def _handle_failure(self, msg, error: str) -> None:
        """Handle message failure and retry logic."""
        if msg.retry_count < self.max_retries:
            # Requirement: "increment the retry count and set status to 'pending'"
            with get_db_connection() as conn:
                conn.execute(
                    'UPDATE scheduled_messages SET status = ?, error_message = ?, retry_count = retry_count + 1 WHERE id = ?',
                    ('pending', error, msg.id),
                )
                conn.commit()
            logger.warning(f"[Backend] Message {msg.id} failed. Retrying ({msg.retry_count + 1}/{self.max_retries}). Error: {error}")
        else:
            # Max retries reached
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
        logger.info(f"[Backend] Scheduler shut down.")
