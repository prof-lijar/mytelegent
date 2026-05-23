from __future__ import annotations

import asyncio
import logging
import sys
from agents.scheduler_agent import SchedulerAgent

# Configure logging to file and console
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(\"logs/activity.log\"),
        logging.StreamHandler(sys.stdout)
    ]
)

async def main():
    \"\"\"Main entry point for the scheduler process.\"\"\"
    print(\"--- tiny-jarvis Scheduler Started ---\")
    print(\"Starting background monitor for scheduled messages...\")
    
    agent = SchedulerAgent(check_interval=60)
    agent.start()
    
    try:
        # Keep the main thread alive while the scheduler runs in the background
        while True:
            await asyncio.sleep(3600)
    except KeyboardInterrupt:
        print(\"\\nStopping scheduler...\")
        agent.stop()
    except Exception as e:
        print(f\"Unexpected error: {e}\")
        agent.stop()

if __name__ == \"__main__\":
    asyncio.run(main())
