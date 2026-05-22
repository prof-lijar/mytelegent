from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from typing import Optional

from pydantic import ValidationError

from schemas.models import ParsedMessageCommand
from tools.config import Config
from tools.local_llm_tool import LocalLLMTool

logger = logging.getLogger(__name__)

class ParsingError(Exception):
    """Raised when the parsing agent fails to extract a valid command."""
    pass

class ParsingAgent:
    """Agent that converts natural language commands into structured ParsedMessageCommand."""

    def __init__(self):
        self.llm = LocalLLMTool()
        with open("prompts/parsing_prompt.md", "r", encoding="utf-8") as f:
            self.parsing_prompt = f.read()
        with open("prompts/refiner_prompt.md", "r", encoding="utf-8") as f:
            self.refiner_prompt = f.read()

    def _resolve_relative_date(self, date_str: str) -> datetime:
        """
        Resolve a date string to a timezone-aware datetime object.
        In a real implementation, this would use a library like dateparser.
        For now, we assume the LLM provides an ISO format or we attempt basic parsing.
        """
        try:
            # Try ISO format first
            return datetime.fromisoformat(date_str)
        except ValueError:
            # If not ISO, we'd normally use dateparser here.
            # As a fallback for this implementation, we'll raise an error 
            # unless the LLM is instructed to provide ISO.
            raise ParsingError(f"Could not resolve date string: {date_str}. Please provide ISO format.")

    def parse_command(self, user_input: str) -> ParsedMessageCommand:
        """
        Parse a natural language command into a ParsedMessageCommand.
        
        Args:
            user_input: The raw text input from the user.
            
        Returns:
            A validated ParsedMessageCommand object.
            
        Raises:
            ParsingError: If the command cannot be parsed or validated.
        """
        current_time = datetime.now(timezone.utc).isoformat()
        
        # Construct the user prompt with context
        full_user_prompt = (
            f"Current Time (UTC): {current_time}\n"
            f"User Timezone: {Config.TIMEZONE}\n\n"
            f"Command: {user_input}\n\n"
            "Return ONLY a JSON object with keys: target, target_type, scheduled_time, message, confidence."
        )

        response = self.llm.call_local_llm(self.parsing_prompt, full_user_prompt)
        
        try:
            return self._extract_json(response)
        except (json.JSONDecodeError, ValidationError, ParsingError) as e:
            logger.warning(f"Initial parsing failed: {e}. Attempting to refine...")
            
            refine_user_prompt = (
                f"The following response was invalid JSON or missing fields:\n{response}\n\n"
                f"Original Command: {user_input}\n\n"
                "Please fix the JSON and return ONLY the corrected JSON object."
            )
            
            refined_response = self.llm.call_local_llm(self.refiner_prompt, refine_user_prompt)
            try:
                return self._extract_json(refined_response)
            except Exception as e2:
                raise ParsingError(f"Failed to parse command after refinement: {e2}")

    def _extract_json(self, text: str) -> ParsedMessageCommand:
        """Extract JSON from LLM response and validate it."""
        # Remove markdown code blocks if present
        clean_text = text.strip()
        if clean_text.startswith("```json"):
            clean_text = clean_text[7:]
        if clean_text.startswith("```"):
            clean_text = clean_text[3:]
        if clean_text.endswith("```"):
            clean_text = clean_text[:-3]
        clean_text = clean_text.strip()

        try:
            data = json.loads(clean_text)
            # The LLM might return the JSON wrapped in a key, handle that
            if isinstance(data, dict) and "command" in data:
                data = data["command"]
            
            # Validate with Pydantic
            command = ParsedMessageCommand(**data)
            
            # Ensure the time is resolved/validated if necessary
            # (Pydantic's datetime handles ISO strings automatically)
            
            return command
        except json.JSONDecodeError as e:
            raise ParsingError(f"Invalid JSON format: {e}")
        except ValidationError as e:
            raise ParsingError(f"JSON missing required fields or invalid values: {e}")
