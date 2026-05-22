from __future__ import annotations
import re
import logging
from datetime import datetime
from typing import Optional

from pydantic import model_validate_json
from tools.local_llm_tool import call_local_llm
from schemas.models import ParsedMessageCommand
from tools.logging_tool import setup_logger

logger = logging.getLogger(__name__)

setup_logger()

class ParsingError(Exception):
    """Raised when command parsing fails"""
    pass


def parse_command(user_input: str) -> ParsedMessageCommand:
    """Parse natural language command into structured ParsedMessageCommand"""
    try:
        # Use the parsing prompt from prompts/parsing_prompt.md
        system_prompt = ("You are an AI that parses natural language commands into\n"
                         "strict JSON format matching the ParsedMessageCommand schema.\n"
                         "Use the current TIMEZONE setting from config.\n"
                         "Respond ONLY with the JSON object. No explanations.\n"
                         "Example: {'target': 'John', 'target_type': 'name',\n                         "'scheduled_time': '2026-05-23T14:30:00+09:00',\n                         "'message': 'Hello'}")

        raw_response = call_local_llm(
            system_prompt=system_prompt,
            user_prompt=user_input
        )

        # Clean up potential LLM response artifacts
        clean_response = raw_response.strip().strip('```json').strip('```').strip('`')

        # Validate and return parsed command
        return model_validate_json(ParsedMessageCommand, clean_response)

    except Exception as e:
        logger.error(f"Parsing failed for input: {user_input}\nError: {str(e)}")
        raise ParsingError(f"Failed to parse command: {str(e)}")


if __name__ == "__main__":
    # Example usage for manual testing
    test_input = "Send 'Hello' to John via name at 2 PM tomorrow"
    try:
        parsed = parse_command(test_input)
        print(f"Parsed: {parsed.model_dump_json(indent=2)}")
    except ParsingError as pe:
        print(f"Error: {str(pe)}")