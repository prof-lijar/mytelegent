from __future__ import annotations

import sys
from datetime import datetime, timezone
from typing import Optional

from agents.parsing_agent import ParsingAgent
from tools.db_tool import initialize_database, insert_scheduled_message
from tools.logging_tool import get_logger

logger = get_logger("main_cli")

def main():
    """Main CLI entry point for tiny-jarvis."""
    initialize_database()
    
    print("--- Tiny Jarvis: AI Telegram Scheduler ---")
    print("Enter a natural language command to schedule a message (or 'exit' to quit).")
    print("Example: 'Tell Jisoo tomorrow at 9 AM that I finished the report'")
    print("-----------------------------------------------------------")

    parser = ParsingAgent()
    
    while True:
        try:
            user_input = input("\nUser: ").strip()
            if not user_input:
                continue
            if user_input.lower() in ("exit", "quit", "q"):
                print("Goodbye!")
                break

            print("Parsing command... please wait...")
            parsed_command = parser.parse_command(user_input)
            
            if parsed_command is None:
                print("Error: Could not parse the command. Please try rephrasing it.")
                logger.error(f"Failed to parse user input: {user_input}")
                continue

            # Present parsed data for confirmation
            print("\n--- Proposed Schedule ---")
            print(f"Recipient: {parsed_command.target} ({parsed_command.target_type})")
            print(f"Message:   {parsed_command.message}")
            print(f"Time:      {parsed_command.scheduled_time.strftime('%Y-%m-%d %H:%M %Z')}")
            print(f"Confidence: {parsed_command.confidence:.2f}")
            print("------------------------")
            
            confirm = input("Confirm schedule? (y/n): ").strip().lower()
            if confirm == 'y':
                try:
                    msg_id = insert_scheduled_message(parsed_command)
                    print(f"Success: Message scheduled successfully (ID: {msg_id}).")
                    logger.info(f"User confirmed and scheduled message: {user_input} -> ID {msg_id}")
                except Exception as e:
                    print(f"Error: Failed to save to database. {e}")
                    logger.error(f"Database error while scheduling: {e}")
                
            else:
                print("Schedule cancelled by user.")
                logger.info(f"User cancelled scheduling for: {user_input}")

        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"Unexpected error: {e}")
            logger.error(f"Unexpected error in main loop: {e}", exc_info=True)

if __name__ == "__main__":
    main()
