from __future__ import annotations

import argparse
import sys
from datetime import datetime
from typing import List

from tools.db_tool import (
    initialize_database, 
    insert_scheduled_message, 
    list_pending_messages, 
    cancel_message
)
from tools.logging_tool import get_logger
from agents.parsing_agent import ParsingAgent
from schemas.models import ParsedMessageCommand, ScheduledMessage

logger = get_logger("main_cli")

def print_header():
    print("\n" + "="*50)
    print("   TINY-JARVIS: AI Telegram Scheduler")
    print("="*50)

def handle_schedule(args, parser: ParsingAgent):
    """Handle the 'schedule' command flow."""
    user_input = args.message
    logger.info(f"Scheduling request received via CLI: {user_input}")
    
    # 1. Parse the command
    parsed_command = parser.parse_command(user_input)
    
    if parsed_command is None:
        print("❌ I couldn't understand that command. Please try rephrasing it.")
        logger.warning(f"Failed to parse user input: {user_input}")
        return

    # 2. Present for confirmation
    print("\n--- Proposed Schedule ---")
    print(f"Recipient: {parsed_command.target} ({parsed_command.target_type})")
    print(f"Message:   {parsed_command.message}")
    print(f"Time:      {parsed_command.scheduled_time.strftime('%Y-%m-%d %H:%M %Z')}")
    print(f"Confidence: {parsed_command.confidence:.2f}")
    print("------------------------")
    
    confirm = input("Confirm scheduling? (y/n): ").strip().lower()
    
    if confirm == 'y':
        # 3. Save to database
        msg_id = insert_scheduled_message(parsed_command)
        print(f"✅ Success! Message scheduled with ID: {msg_id}")
        logger.info(f"Successfully scheduled message {msg_id} for {parsed_command.target}")
    else:
        print("🛑 Scheduling cancelled.")
        logger.info("User cancelled the scheduling request.")

def handle_list():
    """Handle the 'list' command to show pending messages."""
    messages = list_pending_messages()
    if not messages:
        print("No pending messages found.")
        return

    print("\n--- Pending Messages ---")
    print(f"{'ID':<5} {'Recipient':<20} {'Scheduled Time':<25} {'Message':<30}")
    print("-" * 80)
    for msg in messages:
        # Truncate message for display
        display_msg = (msg.message[:27] + '...') if len(msg.message) > 30 else msg.message
        print(f"{msg.id:<5} {msg.target:<20} {msg.scheduled_time.strftime('%Y-%m-%d %H:%M'):<25} {display_msg:<30}")
    print("------------------------")

def handle_cancel(args):
    """Handle the 'cancel' command."""
    success = cancel_message(args.id)
    if success:
        print(f"✅ Message {args.id} has been cancelled.")
        logger.info(f"User cancelled message {args.id}")
    else:
        print(f"❌ Failed to cancel message {args.id}. It may not exist or is no longer pending.")
        logger.warning(f"Failed to cancel message {args.id}")

def handle_run_scheduler():
    """Handle the 'run-scheduler' command."""
    print("Starting scheduler... Use Ctrl+C to stop.")
    import asyncio
    from run_scheduler import main as scheduler_main
    try:
        asyncio.run(scheduler_main())
    except KeyboardInterrupt:
        print("\nStopping scheduler...")

def main():
    # Initialize system
    try:
        initialize_database()
    except Exception as e:
        logger.error(f"Critical error initializing database: {e}")
        print(f"Error: Could not initialize database. See logs/errors.log for details.")
        sys.exit(1)

    parser_agent = ParsingAgent()
    
    cli_parser = argparse.ArgumentParser(description="Tiny-Jarvis AI Telegram Scheduler CLI")
    subparsers = cli_parser.add_subparsers(dest="command", help="Available commands")

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

    # If no arguments, show help
    if len(sys.argv) == 1:
        print_header()
        cli_parser.print_help()
        sys.exit(0)

    args = cli_parser.parse_args()

    if args.command == "schedule":
        handle_schedule(args, parser_agent)
    elif args.command == "list":
        handle_list()
    elif args.command == "cancel":
        handle_cancel(args)
    elif args.command == "run-scheduler":
        handle_run_scheduler()
    else:
        cli_parser.print_help()

if __name__ == "__main__":
    main()
