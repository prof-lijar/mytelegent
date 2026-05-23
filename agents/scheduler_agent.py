from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timezone
from typing import List, Optional

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from tools.db_tool import (
    get_due_messages,
    mark_processing,
    mark_sent,
    mark_failed,
    get_message_by_id,
    update_message_status,
)
from tools.telegram_tool import send_telegram_message
from tools.logging_tool import logger

# Configure logging
logger.setLevel(logging.INFO)

class SchedulerAgent:
    \"\"\"Agent that manages the scheduling and sending of messages.\"\"\"

    def __init__(self, max_retries: int = 2) -> None:
        \"\"\"Initialize the scheduler agent.\"\"\"
        self.max_retries = max_retries
        self.scheduler = AsyncIOScheduler()

    async def start(self) -> None:
        \"\"\"Start the background scheduler.\"\"\"
        self.scheduler.add_job(
            self._check_due_messages, 
            'interval', 
            seconds=60, 
            id='check_due_messages_job', 
            replace_existing=True
        )
        self.scheduler.start()
        logger.info(\"[Backend] SchedulerAgent started. Checking for due messages every 60 seconds.\")

    async def stop(self) -> None:
        \"\"\"Stop the background scheduler.\"\"\"
        self.scheduler.shutdown()
        logger.info(\"[Backend] SchedulerAgent stopped.\")

    async def _check_due_messages(self) -> None:
        \"\"\"Periodically check the database for due messages.\"\"\"
        now = datetime.now(timezone.utc)
        due_messages = get_due_messages(now)
        
        if not due_messages:
            return

        logger.info(f\"[Backend] Found {len(due_messages)} due messages. Processing...\")
        
        # Process messages sequentially as per requirements
        for msg in due_messages:
            await self._process_message(msg)

    async def _process_message(self, msg) -> None:
        \"\"\"Handle the sending logic for a single message.\"\"\"
        try:
            # 1. Mark as processing
            mark_processing(msg.id)
            
            # 2. Send message via Telegram tool
            # Note: send_telegram_message already includes the 2-5s random delay
            result = await send_telegram_message(msg.target, msg.message)
            
            if result[\"success\"]:
                mark_sent(msg.id)
                logger.info(f\"[Backend] Successfully sent message {msg.id} to {msg.target}\")
            else:
                # Handle failure
                error_msg = result.get(\"error\", \"Unknown error\")
                logger.warning(f\"[Backend] Failed to send message {msg.id} to {msg.target}: {error_msg}\")
                await self._handle_failure(msg.id, error_msg)
                
        except Exception as e:
            error_msg = str(e)
            logger.error(f\"[Backend] Unexpected error processing message {msg.id}: {error_msg}\")
            await self._handle_failure(msg.id, error_msg)

    async def _handle_failure(self, message_id: int, error: str) -> None:
        \"\"\"Update database status based on retry count.\"\"\"
        # 1. Increment retry count and mark as failed (using db_tool.mark_failed)
        mark_failed(message_id, error)
        
        # 2. Check current retry count
        msg = get_message_by_id(message_id)
        if msg is None:
            return
        
        # 3. If retry count is within limit, set status back to 'pending' for next check
        if msg.retry_count <= self.max_retries:
            update_message_status(message_id, 'pending', error_message=error)
            logger.info(f\"[Backend] Message {message_id} will be retried (retry {msg.retry_count}/{self.max_retries})\")
        else:
            logger.error(f\"[Backend] Message {message_id} reached max retries and is marked as failed.\")

    async def run_forever(self) -> None:
        \"\"\"Run the scheduler in a blocking way for the entry point.\"\"\"
        await self.start()
        try:
            while True:
                await asyncio.sleep(3600)
        except asyncio.CancelledError:
            await self.stop()
