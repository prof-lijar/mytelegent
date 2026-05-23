from __future__ import annotations

import asyncio
import logging
import random
from datetime import datetime, timezone
from typing import NoReturn

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from tools.db_tool import get_due_messages, mark_processing, mark_sent, mark_failed
from tools.telegram_tool import send_telegram_message
from tools.logging_tool import get_logger

logger = get_logger(__name__)

class SchedulerAgent:
    \"\"\"Agent responsible for scheduling and sending messages via Telegram.\"\"\"

    def __init__(self, check_interval: int = 60) -> None:
        \"\"\"Initialize the SchedulerAgent.\"\"\"
        self.scheduler = AsyncIOScheduler()
        self.check_interval = check_interval
        self.max_retries = 2

    async def process_due_messages(self) -> None:
        \"\"\"Check for due messages and attempt to send them.\"\"\"
        now = datetime.now(timezone.utc)
        due_messages = get_due_messages(now)
        
        if not due_messages:
            return

        logger.info(f\"[Backend] Found {len(due_messages)} messages due for sending\")

        for msg in due_messages:
            try:
                # Mark as processing to avoid duplicate sends
                mark_processing(msg.id)
                
                logger.info(f\"[Backend] Attempting to send message {msg.id} to {msg.target}\")
                
                # The Telegram tool already implements the 2-5s random delay
                result = await send_telegram_message(msg.target, msg.message)
                
                if result[\"success\"]:
                    mark_sent(msg.id)
                    logger.info(f\"[Backend] Successfully sent message {msg.id} to {msg.target}\")
                else:
                    error_msg = result.get(\"error\", \"Unknown error\")
                    await self._handle_failure(msg, error_msg)
                    
            except Exception as e:
                logger.exception(f\"[Backend] Unexpected error processing message {msg.id}: {e}\")
                await self._handle_failure(msg, str(e))

    async def _handle_failure(self, msg, error_msg: str) -> None:
        \"\"\"Handle message sending failure with retry logic.\"\"\"
        if msg.retry_count < self.max_retries:
            logger.warning(f\"[Backend] Message {msg.id} failed. Retry {msg.retry_count + 1}/{self.max_retries}. Error: {error_msg}\")
            # We want to set it back to 'pending' so it's picked up again.
            # Since mark_failed sets it to 'failed', we need a way to set it to 'pending'.
            # I will implement a custom update in db_tool or just call mark_failed and then update.
            # For now, I'll call mark_failed and then I'll fix db_tool to support retries better.
            mark_failed(msg.id, error_msg)
            # To allow retry, we must set it back to 'pending'
            from tools.db_tool import get_db_connection
            with get_db_connection() as conn:
                conn.execute(
                    'UPDATE scheduled_messages SET status = ? WHERE id = ?',
                    ('pending', msg.id),
                )
                conn.commit()
        else:
            logger.error(f\"[Backend] Message {msg.id} failed after {self.max_retries} retries. Marking as failed. Error: {error_msg}\")
            mark_failed(msg.id, error_msg)

    def start(self) -> None:
        \"\"\"Start the scheduler.\"\"\"
        self.scheduler.add_job(self.process_due_messages, 'interval', seconds=self.check_interval)
        self.scheduler.start()
        logger.info(f\"[Backend] Scheduler started with interval {self.check_interval}s\")

    def shutdown(self) -> None:
        \"\"\"Shutdown the scheduler.\"\"\"
        self.scheduler.shutdown()
        logger.info(\"[Backend] Scheduler shut down\")
