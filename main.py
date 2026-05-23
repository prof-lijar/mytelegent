from __future__ import annotations

import sys
from pathlib import Path

from agents.parsing_agent import ParsingAgent
from tools.db_tool import initialize_database, insert_scheduled_message
from tools.logging_tool import get_logger

logger = get_logger("main_cli")

def print_header():
    """Prints a simple CLI header."""
    print("\\n" + "="*40)
    print("  TINY-JARVIS: Personal AI Agent")
    print("="*40)

def main():
    """Main entry point for the Tiny-Jarvis CLI."""
    # Initialize DB
    try:
        initialize_database()
        logger.info("CLI started and database initialized.")
    except Exception as e:
        logger.error(f"Failed to initialize database during CLI startup: {e}", exc_info=True)
        print("Error: Database initialization failed. Check logs/errors.log.")
        sys.exit(1)

    # Initialize Parsing Agent
    try:
        parser = ParsingAgent()
        logger.info("Parsing agent initialized successfully.")
    except Exception as e:
        logger.error(f"Failed to initialize parsing agent: {e}", exc_info=True)
        print("Error: Parsing agent initialization failed. Check logs/errors.log.")
        sys.exit(1)

    print_header()
    
    while True:
        try:
            user_input = input("\n Enter a command (or 'exit' to quit): ").strip()
            if not user_input:
                continue
            if user_input.lower() in ('exit', 'quit', 'q'):
                print("Goodbye!")
                break
            
            logger.info(f"User input received: {user_input}")
            
            # 1. Parse the command
            parsed = parser.parse_command(user_input)
            
            if parsed is None:
                logger.warning(f"Failed to parse input: {user_input}")
                print("Could not understand the command. Please rephrase it.")
                continue
            
            # 2. Present for confirmation
            print("\n--- Parsed Command ---")
            print(f"Recipient: {parsed.target} ({parsed.target_type})")
            print(f"Message:   {parsed.message}")
            print(f"Scheduled: {parsed.scheduled_time}")
            print(f"Confidence: {parsed.confidence:.2f}")
            print("----------------------")
            
            confirm = input("Confirm scheduling? (y/n): ").strip().lower()
            if confirm != 'y':
                logger.info("User declined to schedule the message.")
                print("Command cancelled.")
                continue
            
            # 3. Save to database
            try:
                msg_id = insert_scheduled_message(parsed)
                logger.info(f"Successfully scheduled message {msg_id} for {parsed.target}.")
                print(f"Success! Message scheduled with ID: {msg_id}")
            except Exception as e:
                logger.error(f"Database error while scheduling: {e}", exc_info=True)
                print("Error: Failed to save message to database. Check logs/errors.log.")
                
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            logger.error(f"Unexpected error in CLI loop: {e}", exc_info=True)
            print("An unexpected error occurred. Check logs/errors.log.")

if __name__ == "__main__":
    main()
