from __future__ import annotations

import sys
from datetime import datetime
from tools.db_tool import initialize_database, insert_scheduled_message
from tools.logging_tool import get_logger
from agents.parsing_agent import ParsingAgent
from schemas.models import ParsedMessageCommand

logger = get_logger("main_cli")

def print_header():
    print("\n" + "="*50)
    print("   TINY-JARVIS: AI Telegram Scheduler")
    print("="*50)
    print("Enter a command (e.g., 'Tell Jisoo tomorrow at 9 AM that I finished the report')")
    print("Type 'exit' or 'quit' to stop.\n")

def main():
    # Initialize system
    try:
        initialize_database()
    except Exception as e:
        logger.error(f"Critical error initializing database: {e}")
        print(f"Error: Could not initialize database. See logs/errors.log for details.")
        sys.exit(1)

    parser = ParsingAgent()
    print_header()

    while True:
        try:
            user_input = input(">>> ").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() in ['exit', 'quit']:
                print("Exiting Tiny-Jarvis. Goodbye!")
                break

            logger.info(f"User input received: {user_input}")
            
            # 1. Parse the command
            parsed_command = parser.parse_command(user_input)
            
            if parsed_command is None:
                print("❌ I couldn't understand that command. Please try rephrasing it.")
                logger.warning(f"Failed to parse user input: {user_input}")
                continue

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
                print("🚫 Scheduling cancelled.")
                logger.info("User cancelled the scheduling request.")
            
            print("\n")

        except KeyboardInterrupt:
            print("\nExiting Tiny-Jarvis. Goodbye!")
            break
        except Exception as e:
            logger.error(f"Unexpected error in CLI loop: {e}", exc_info=True)
            print(f"An unexpected error occurred. Please check logs/errors.log")

if __name__ == "__main__":
    main()
