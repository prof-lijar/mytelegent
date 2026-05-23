from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from typing import Optional

from pydantic import ValidationError
from schemas.models import ParsedMessageCommand
from tools.local_llm_tool import LocalLLMTool
from tools.config import Config
from tools.logging_tool import get_logger

logger = get_logger("parsing_agent")

class ParsingAgent:
    """Agent that converts natural language commands into structured JSON using a local LLM."""

    def __init__(self):
        self.llm_tool = LocalLLMTool()
        try:
            with open('prompts/parsing_prompt.md', 'r', encoding='utf-8') as f:
                self.system_prompt = f.read()
        except FileNotFoundError:
            logger.error('Parsing prompt file not found. Falling back to a basic prompt.')
            self.system_prompt = (
                'You are a specialized NLP agent that converts natural language scheduling commands into structured JSON. '
                'Return ONLY a valid JSON object matching the ParsedMessageCommand schema.'
            )

    def parse_command(self, user_input: str) -> Optional[ParsedMessageCommand]:
        """Parse a natural language command into a ParsedMessageCommand object."""
        current_time = datetime.now(timezone.utc).isoformat()
        timezone_str = Config.TIMEZONE
        
        user_prompt = (
            f'Current Time: {current_time}\n'
            f'Timezone: {timezone_str}\n'
            f'User Command: \"{user_input}\"\n'
        )
        
        try:
            response = self.llm_tool.call_local_llm(self.system_prompt, user_prompt)
            cleaned_response = self._clean_json_response(response)
            data = json.loads(cleaned_response)
            return ParsedMessageCommand(**data)
        except (json.JSONDecodeError, ValidationError, Exception) as e:
            logger.error(f'Parsing failed for input {user_input}: {e}', exc_info=True)
            return None

    def _clean_json_response(self, response: str) -> str:
        """Remove markdown code blocks from the LLM response."""
        response = response.strip()
        if response.startswith('```json') and response.endswith('```'):
            return response[8:-3].strip()
        elif response.startswith('```') and response.endswith('```'):
            return response[4:-3].strip()
        elif response.startswith('{') and response.endswith('}'):
            return response
        else:
            start = response.find('{')
            end = response.rfind('}')
            if start != -1 and end != -1:
                return response[start:end+1]
            return response

if __name__ == '__main__':
    # Example usage
    agent = ParsingAgent()
    test_input = 'Send Hello to @johndoe tomorrow at 9 AM'
    result = agent.parse_command(test_input)
    print(f'Input: {test_input}\nResult: {result}')
