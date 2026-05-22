import unittest
from unittest.mock import patch, MagicMock

from agents.parser import MessageParser, ParsingError
from schemas.models import ParsedMessageCommand


class TestMessageParser(unittest.TestCase):
    """Test suite for the MessageParser class"""

    def setUp(self):
        self.parser = MessageParser()

    @patch('agents.parser.LocalLLMTool')
    def test_valid_parsing(self, mock_llm):
        """Test successful parsing of a valid command"""
        # Arrange
        mock_response = '{"target": "John Doe", "target_type": "name", "scheduled_time": "2026-05-23T09:00:00+09:00", "message": "Good morning"}'
        mock_llm.return_value.call_local_llm.return_value = mock_response

        # Act
        result = self.parser.parse("Send 'Good morning' to John Doe tomorrow at 9am")

        # Assert
        self.assertIsInstance(result, ParsedMessageCommand)
        self.assertEqual(result.target, "John Doe")
        self.assertEqual(result.message, "Good morning")

    @patch('agents.parser.LocalLLMTool')
    def test_invalid_json(self, mock_llm):
        """Test parsing failure due to invalid JSON from LLM"""
        # Arrange
        mock_response = '{invalid: json}'
        mock_llm.return_value.call_local_llm.return_value = mock_response

        # Act & Assert
        with self.assertRaises(ParsingError):
            self.parser.parse("Send test message")

    @patch('agents.parser.LocalLLMTool')
    def test_llm_error_response(self, mock_llm):
        """Test LLM returns explicit error in response"""
        # Arrange
        error_response = '{"error": "Could not parse time expression"}'
        mock_llm.return_value.call_local_llm.return_value = error_response

        # Act & Assert
        with self.assertRaises(ParsingError):
            self.parser.parse("Invalid command with bad time format")

if __name__ == '__main__':
    unittest.main()