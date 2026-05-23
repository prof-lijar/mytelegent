from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timezone
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from tools import db_tool, telegram_tool

# Setup logging
logger = logging.getLogger(__name__)

class SchedulerAgent:
    \"\"\"Background agent that monitors and sends scheduled messages.\"\"\"

    def __init__(self, check_interval: int = 60) -> None:
        \"\"\"Initialize the SchedulerAgent.\"\"\"
        self.scheduler = AsyncIOScheduler()
        self.check_interval = check_interval

    async def check_and_send_messages(self) -> None:
        \"\"\"Check for due messages and send them.\"\"\"
        now = datetime.now(timezone.utc)
        due_messages = db_tool.get_due_messages(now)
        
        if not due_messages:
            return

        logger.info(f\"[Backend] Found {len(due_messages)} due messages. Processing...\")

        for msg in due_messages:
            try:
                db_tool.mark_processing(msg.id)
                logger.info(f\"[Backend] Attempting to send message {msg.id} to {msg.target}\")
                
                result = await telegram_tool.send_telegram_message(msg.target, msg.message)
                
                if result[\"success\"]:
                    db_tool.mark_sent(msg.id)
                    logger.info(f\"[Backend] Successfully sent message {msg.id}\")
                else:
                    error = result.get(\"error\") or \"Unknown error\"
                    if msg.retry_count < 2:
                        db_tool.mark_retry(msg.id, error)
                        logger.warning(f\"[Backend] Message {msg.id} failed, scheduled for retry. Error: {error}\")
                    else:
                        db_tool.mark_failed(msg.id, error)
                        logger.error(f\"[Backend] Message {msg.id} failed after max retries. Error: {error}\")
                        
            except Exception as e:
                logger.exception(f\"[Backend] Unexpected error processing message {msg.id}: {e}\")
                db_tool.mark_retry(msg.id, str(e)) if msg.retry_count < 2 else db_tool.mark_failed(msg.id, str(e))

    def start(self) -> None:
        \"\"\"Start the scheduler.\"\"\"
        self.scheduler.add_job(
            self.check_and_send_messages, 
            'interval', 
            seconds=self.check_interval
        )
        self.scheduler.start()
        logger.info(f\"[Backend] Scheduler started. Checking every {self.check_interval} seconds.\")

    def stop(self) -> None:
        \"\"\"Stop the scheduler.\"\"\"
        self.scheduler.shutdown()
        logger.info(\"[Backend] Scheduler stopped.\")

if __name__ == \"__main__\":
    # Simple manual test
    async def main():
        agent = SchedulerAgent(check_interval=10)
        agent.start()
        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            agent.stop()
    
    asyncio.run(main())
