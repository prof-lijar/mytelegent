from __future__ import annotations

import argparse
import sys
import asyncio
from typing import List, Optional
from datetime import datetime
from tools.db_tool import initialize_database, insert_scheduled_message, list_pending_messages, cancel_message
from tools.logging_tool import get_logger
from agents.parsing_agent import ParsingAgent
from agents.scheduler_agent import SchedulerAgent

logger = get_logger("main_cli")

def handle_schedule(message: str, parser: ParsingAgent) -> None:
    """Handle the scheduling of a message with confirmation flow."""
    logger.info(f"Scheduling request received: {message}")
    
    # 1. Parse the command
    parsed_command = parser.parse_command(message)
    
    if parsed_command is None:
        print("❌ I couldn't understand that command. Please try rephrasing it.")
        logger.warning(f"Failed to parse user input: {message}")
        return

    # 2. Present for confirmation
    print("\n--- Proposed Schedule ---")
    print(f"Recipient: {parsed_command.target} ({parsed_command.target_type})")
    print(f"Message:   {parsed_command.message}")
    print(f"Time:      {parsed_command.scheduled_time.strftime('%Y-%m-%d %H:%M %Z')}")
    print(f"Confidence: {parsed_command.confidence:.2f}")
    print("--------------------------------")
    
    try:
        confirm = input("Confirm scheduling? (y/n): ").strip().lower()
    except EOFError:
        print("\nNo input detected. Scheduling cancelled.")
        return
    
    if confirm == 'y':
        # 3. Save to database
        msg_id = insert_scheduled_message(parsed_command)
        print(f"✅ Success! Message scheduled with ID: {msg_id}")
        logger.info(f"Successfully scheduled message {msg_id} for {parsed_command.target}")
    else:
        print("🚫 Scheduling cancelled.")
        logger.info("User cancelled the scheduling request.")

def handle_list() -> None:
    """List all pending messages."""
    messages = list_pending_messages()
    if not messages:
        print("No pending messages found.")
        return

    print("\n--- Pending Messages ---")
    print(f"{'ID':<5} {'Recipient':<20} {'Time':<25} {'Message'}")
    print("-" * 70)
    for msg in messages:
        # Truncate message for display
        display_msg = (msg.message[:30] + '...') if len(msg.message) > 30 else msg.message
        print(f"{msg.id:<5} {msg.target:<20} {msg.scheduled_time.strftime('%Y-%m-%d %H:%M'):<25} {display_msg}")
    print("-" * 70)

def handle_cancel(message_id: int) -> None:
    """Cancel a scheduled message by ID."""
    success = cancel_message(message_id)
    if success:
        print(f"✅ Message {message_id} has been cancelled.")
        logger.info(f"Cancelled scheduled message {message_id}")
    else:
        print(f"❌ Could not find pending message with ID {message_id}.")
        logger.warning(f"Failed to cancel message {message_id}: not found or not pending")

async def run_scheduler_process() -> None:
    """Start the background scheduler process."""
    try:
        agent = SchedulerAgent()
        agent.start()
        print("tiny-jarvis Scheduler is running... (Ctrl+C to stop)")
        while True:
            await asyncio.sleep(3600)
    except asyncio.CancelledError:
        print("\nScheduler cancelled.")
    except Exception as e:
        logger.error(f"Unexpected error in scheduler process: {e}", exc_info=True)
        print(f"Unexpected error: {e}")
        sys.exit(1)

def main(argv: Optional[List[str]] = None) -> None:
    # Initialize system
    try:
        initialize_database()
    except Exception as e:
        logger.error(f"Critical error initializing database: {e}")
        print(f"Error: Could not initialize database. See logs/errors.log for details.")
        sys.exit(1)

    parser_arg = argparse.ArgumentParser(
        description="tiny-jarvis: AI Telegram Scheduler CLI"
    )
    subparsers = parser_arg.add_subparsers(dest="command", help="Available commands")

    # Schedule command
    sched_parser = subparsers.add_parser("schedule", help="Schedule a new message")
    sched_parser.add_argument("message", type=str, help="The natural language command to schedule")

    # List command
    subparsers.add_parser("list", help="List all pending messages")

    # Cancel command
    cancel_parser = subparsers.add_parser("cancel", help="Cancel a scheduled message")
    cancel_parser.add_argument("id", type=int, help="The ID of the message to cancel")

    # Run-scheduler command
    subparsers.add_parser("run-scheduler", help="Start the background scheduler process")

    args = parser_arg.parse_args(argv)

    if args.command == "schedule":
        parsing_agent = ParsingAgent()
        handle_schedule(args.message, parsing_agent)
    elif args.command == "list":
        handle_list()
    elif args.command == "cancel":
        handle_cancel(args.id)
    elif args.command == "run-scheduler":
        try:
            asyncio.run(run_scheduler_process())
        except KeyboardInterrupt:
            print("\nStopping scheduler...")
    else:
        parser_arg.print_help()

if __name__ == "__main__":
    main(sys.argv[1:])
