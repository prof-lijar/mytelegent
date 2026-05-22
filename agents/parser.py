from __future__ import annotations

from pydantic import ValidationError
from typing import Optional

from tools.local_llm_tool import LocalLLMTool
from schemas.models import ParsedMessageCommand


class MessageParser:
    """Parses natural language commands into structured ParsedMessageCommand objects"""

    def __init__(self):
        self.llm = LocalLLMTool()
        self.system_prompt = self._build_system_prompt()

    def _build_system_prompt(self) -> str:
        """Construct the system prompt that enforces strict JSON output"""
        return """
        You are a message parsing agent. Your task is to parse natural language commands
        into strict JSON format matching the ParsedMessageCommand schema.

        Rules:
        1. Output ONLY valid JSON. No explanations, no markdown, no extra text.
        2. Parse the input into target, target_type, scheduled_time, message.
        3. For time phrases like 'in 2 hours', calculate absolute datetime in user's timezone.
        4. If parsing fails, output {"error": "Invalid command format"}
        """

    def parse(self, text: str) -> ParsedMessageCommand:
        """Parse natural language text into a structured message command"""
        try:
            response = self.llm.call_local_llm(
                system_prompt=self.system_prompt,
                user_prompt=text
            )

            if response.startswith("{\"error\""):  # Check for LLM self-reported errors
                raise ValueError("LLM parsing failed")

            return ParsedMessageCommand.model_validate_json(response)

        except (ValidationError, ValueError) as e:
            raise ParsingError(f"Failed to parse command: {text}\nError: {str(e)}") from e

class ParsingError(Exception):
    """Error raised when command parsing fails"""
    pass