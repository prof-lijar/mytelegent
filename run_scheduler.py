from __future__ import annotations

import asyncio
import logging
import sys
from agents.scheduler_agent import SchedulerAgent

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger("RunScheduler")

async def main() -> None:
    \"\"\"Entry point to start the scheduler agent.\"\"\"
    agent = SchedulerAgent()
    try:
        agent.start()
        logger.info("[Backend] Scheduler process started. Press Ctrl+C to exit.")
        
        # Keep the main thread alive while the scheduler runs in the background
        while True:
            await asyncio.sleep(3600)
    except (KeyboardInterrupt, SystemExit):
        logger.info("[Backend] Scheduler shutting down...")
        agent.shutdown()
    except Exception as e:
        logger.exception(f"[Backend] Fatal error in scheduler process: {e}")
        agent.shutdown()

if __name__ == \"__main__\":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
