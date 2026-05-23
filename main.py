from __future__ import annotations

import sys
from pathlib import Path

from agents.parsing_agent import ParsingAgent
from tools.db_tool import initialize_database, insert_scheduled_message
from tools.logging_tool import get_logger

logger = get_logger("main_cli")

def main() -> None:
    \"\"\"Main entry point for the tiny-jarvis CLI.\"\"\"
    # Initialize DB
    initialize_database()
    
    print(\"--- tiny-jarvis AI Agent CLI ---\")
    print(\"Enter a natural language command to schedule a message (or 'exit' to quit).\")
    print(\"Example: 'Tell Jisoo tomorrow at 9 AM that I finished the report'\")
    print(\"----------------------------------------------------------------------\")

    parser = ParsingAgent()

    while True:
        try:
            user_input = input(\"\\n> \").strip()
            if not user_input:
                continue
            if user_input.lower() in (\"exit\", \"quit\", \"q\"):
                print(\"Exiting...\")
                break

            print(\"Parsing your command...\", end=\" \", flush=True)
            parsed_cmd = parser.parse_command(user_input)
            
            if parsed_cmd is None:
                print(\"Failed. Please rephrase your command.\")
                logger.warning(f\"User command parsing failed: {user_input}\")
                continue
            
            print(\"Done!\", flush=True)
            
            # Display parsed results for confirmation
            print(\"\\n--- Parsed Command Details ---\")
            print(f\"Recipient: {parsed_cmd.target} ({parsed_cmd.target_type})\")
            print(f\"Scheduled Time: {parsed_cmd.scheduled_time.strftime('%Y-%m-%d %H:%M:%S %Z')}\")
            print(f\"Message: {parsed_cmd.message}\")
            print(f\"Confidence: {parsed_cmd.confidence:.2f}\")
            print(\"-----------------------------\")
            
            confirm = input(\"Confirm scheduling? (y/n): \").lower().strip()
            if confirm == 'y':
                msg_id = insert_scheduled_message(parsed_cmd)
                print(f\"\\nSuccess! Message scheduled with ID: {msg_id}\")
                logger.info(f\"User confirmed and scheduled message: {user_input} -> ID: {msg_id}\")
            else:
                print(\"\\nCommand cancelled by user.\")
                logger.info(f\"User cancelled scheduling for command: {user_input}\")
            
        except KeyboardInterrupt:
            print(\"\\nExiting...\")
            break
        except Exception as e:
            print(f\"\\nUnexpected error: {e}\")
            logger.error(f\"Unexpected error in CLI loop: {e}\", exc_info=True)

if __name__ == \"__main__\":
    main()
