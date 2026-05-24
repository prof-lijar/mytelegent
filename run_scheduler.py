from __future__ import annotations

import asyncio
import sys
from agents.scheduler_agent import SchedulerAgent

async def main() -> None:
    """Entry point to start the background scheduler agent."""
    try:
        agent = SchedulerAgent()
        agent.start()
        
        print("tiny-jarvis Scheduler is running... (Ctrl+C to stop)")
        
        # Keep the event loop running
        while True:
            await asyncio.sleep(3600)
    except asyncio.CancelledError:
        print("\nScheduler cancelled.")
    except KeyboardInterrupt:
        print("\nStopping scheduler...")
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nStopping scheduler...")
