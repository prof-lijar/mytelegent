from __future__ import annotations

import asyncio
import signal
import sys
from tools.logging_tool import setup_logging, get_logger
from agents.scheduler_agent import SchedulerAgent

logger = get_logger(__name__)

async def main() -> None:
    \"\"\"Main entry point for the background scheduler process.\"\"\"
    setup_logging()
    logger.info(\"[Backend] Starting the Scheduler Process...\")
    
    scheduler_agent = SchedulerAgent()
    scheduler_agent.start()
    
    try:
        # Keep the process alive
        while True:
            await asyncio.sleep(3600)
    except asyncio.CancelledError:
        logger.info(\"[Backend] Scheduler process cancelled.\")
    except KeyboardInterrupt:
        logger.info(\"[Backend] Scheduler process interrupted by user.\")
    finally:
        scheduler_agent.shutdown()
        logger.info(\"[Backend] Scheduler process exited.\")

if __name__ == \"__main__\":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        # Avoid printing traceback on Ctrl+C
        sys.exit(0)
