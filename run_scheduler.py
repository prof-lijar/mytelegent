import asyncio
import logging
from agents.scheduler_agent import SchedulerAgent
from tools.logging_tool import logger

# Configure logging
logging.basicConfig(level=logging.INFO)

async def main():
    \"\"\"Entry point to start the scheduler background process.\"\"\"
    logger.info(\"[Backend] Starting scheduler runner... \")
    
    scheduler_agent = SchedulerAgent()
    try:
        await scheduler_agent.run_forever()
    except KeyboardInterrupt:
        await scheduler_agent.stop()
        logger.info(\"[Backend] Scheduler runner stopped by user.\")
    except Exception as e:
        logger.error(f\"[Backend] Fatal error in scheduler runner: {e}\")

if __name__ == \"__main__\":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
