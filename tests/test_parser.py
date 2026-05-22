import pytest
from unittest.mock import patch, Mock
from agents.parsing_agent import parse_command, ParsingError
from datetime import datetime
from pydantic import ValidationError


def test_valid_command_parsing():
    mock_response = '{"target": "John", "target_type": "name", "scheduled_time": "2026-05-23T14:30:00+09:00", "message": "Hello"}'
    
    with patch("agents.parsing_agent.call_local_llm", return_value=mock_response):
        result = parse_command("Send 'Hello' to John via name at 2 PM tomorrow")
        assert result.target == "John"
        assert result.target_type == "name"
        assert result.scheduled_time == datetime.fromisoformat("2026-05-23T14:30:00+09:00")
        assert result.message == "Hello"


def test_invalid_json_parsing():
    mock_response = "{invalid: json}"
    with patch("agents.parsing_agent.call_local_llm", return_value=mock_response), pytest.raises(ParsingError):
        parse_command("Invalid command")

def test_validation_error():
    mock_response = '{"target": 123, "target_type": "name", "scheduled_time": "invalid-date", "message": "Hello"}'
    with patch("agents.parsing_agent.call_local_llm", return_value=mock_response), pytest.raises(ParsingError):
        parse_command("Invalid command")

def test_empty_input():
    with pytest.raises(ParsingError):
        parse_command("")

if __name__ == "__main__":
    pytest.main()