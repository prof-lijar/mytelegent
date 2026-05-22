from __future__ import annotations

import pytest
from unittest.mock import MagicMock, patch
from agents.parsing_agent import ParsingAgent
from schemas.models import ParsedMessageCommand

def test_parsing_agent_success():
    """Test successful parsing of a natural language command."""
    # Mock the LocalLLMTool.call_local_llm method
    with patch("agents.parsing_agent.LocalLLMTool") as MockLLMTool:
        mock_llm = MockLLMTool.return_value
        # Simulate a valid JSON response from the LLM
        mock_llm.call_local_llm.return_value = (
            '{\n'
            '  "target": "johndoe",\n'
            '  "target_type": "username",\n'
            '  "scheduled_time": "2026-05-23T00:00:00Z",\n'
            '  "message": "Happy Birthday!",\n'
            '  "confidence": 1.0\n'
            '}'
        )
        
        agent = ParsingAgent()
        result = agent.parse_command("Send 'Happy Birthday!' to @johndoe tomorrow at 9 AM")
        
        assert result is not None
        assert isinstance(result, ParsedMessageCommand)
        assert result.target == "johndoe"
        assert result.target_type == "username"
        assert result.message == "Happy Birthday!"
        assert result.confidence == 1.0

def test_parsing_agent_markdown_response():
    """Test parsing when the LLM returns JSON wrapped in markdown code blocks."""
    with patch("agents.parsing_agent.LocalLLMTool") as MockLLMTool:
        mock_llm = MockLLMTool.return_value
        mock_llm.call_local_llm.return_value = (
            '```json\n'
            '{\n'
            '  "target": "alice",\n'
            '  "target_type": "name",\n'
            '  "scheduled_time": "2026-05-23T12:00:00Z",\n'
            '  "message": "Lunch tomorrow?",\n'
            '  "confidence": 0.9\n'
            '}\n'
            '```'
        )
        
        agent = ParsingAgent()
        result = agent.parse_command("Send 'Lunch tomorrow?' to Alice")
        
        assert result is not None
        assert result.target == "alice"
        assert result.target_type == "name"

def test_parsing_agent_invalid_json():
    """Test handling of invalid JSON response from the LLM."""
    with patch("agents.parsing_agent.LocalLLMTool") as MockLLMTool:
        mock_llm = MockLLMTool.return_value
        mock_llm.call_local_llm.return_value = "This is not JSON at all."
        
        agent = ParsingAgent()
        result = agent.parse_command("Something weird")
        
        assert result is None

def test_parsing_agent_pydantic_validation_error():
    """Test handling of LLM response that is valid JSON but fails Pydantic validation."""
    with patch("agents.parsing_agent.LocalLLMTool") as MockLLMTool:
        mock_llm = MockLLMTool.return_value
        mock_llm.call_local_llm.return_value = (
            '{\n'
            '  "target": "bob",\n'
            '  "target_type": "invalid_type",\n'
            '  "scheduled_time": "2026-05-23T12:00:00Z",\n'
            '  "message": "Hello",\n'
            '  "confidence": 1.5\n'
            '}'
        )
        
        agent = ParsingAgent()
        result = agent.parse_command("Send Hello to Bob")
        
        assert result is None

def test_parsing_agent_prompt_file_missing():
    """Test ParsingAgent initialization when the prompt file is missing."""
    with patch("builtins.open", side_effect=FileNotFoundError):
        agent = ParsingAgent()
        # Should not crash, should use fallback prompt
        assert agent.system_prompt is not None
        assert "structured JSON" in agent.system_prompt
