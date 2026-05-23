import os
import sqlite3
import pytest
from datetime import datetime
from tools.db_tool import initialize_database, insert_scheduled_message
from tools.logging_tool import get_logger
from agents.parsing_agent import ParsingAgent
from schemas.models import ParsedMessageCommand
from tools.telegram_tool import send_telegram_message
from unittest.mock import AsyncMock, patch, MagicMock
import asyncio

logger = get_logger("e2e_validation")

@pytest.mark.asyncio
async def test_full_system_e2e():
    # 1. Setup
    # Use a dedicated test database for E2E
    test_db_path = "database/messages_e2e.db"
    if os.path.exists(test_db_path):
        os.remove(test_db_path)
    
    # Mock LLM response to avoid depending on real LLM
    mock_llm_response = '{"target": "Jisoo", "target_type": "username", "message": "I finished the report", "scheduled_time": "2026-05-24T09:00:00+00:00", "confidence": 0.95}'
    
    # Patch the Config.DB_PATH to use the test DB
    with patch('tools.config.Config.DB_PATH', test_db_path), \
         patch('tools.local_llm_tool.call_local_llm', return_value=mock_llm_response):
        
        initialize_database()
        
        # 2. Natural Language Input -> Parsing
        parser = ParsingAgent()
        user_input = "Tell Jisoo tomorrow at 9 AM that I finished the report"
        
        parsed_command = parser.parse_command(user_input)
        assert parsed_command is not None, "Parsing failed!"
        assert parsed_command.target == "Jisoo"
        assert "finished the report" in parsed_command.message
        
        # 3. Confirmation and Storage
        msg_id = insert_scheduled_message(parsed_command)
        assert msg_id is not None, "Database insertion failed!"
        
        # 4. Verify Database State
        conn = sqlite3.connect(test_db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM scheduled_messages WHERE id = ?", (msg_id,))
        row = cursor.fetchone()
        conn.close()
        
        assert row is not None, "Database verification failed: Message not found!"
        
        # 5. Trigger Scheduler and Verify Send Action
        # Patch the get_due_messages to return the message we just created
        with patch('tools.db_tool.get_due_messages', return_value=[
            ParsedMessageCommand(
                target=parsed_command.target,
                target_type=parsed_command.target_type,
                message=parsed_command.message,
                scheduled_time=datetime.now(),
                confidence=parsed_command.confidence
            )
        ]):
            # Mock the Telegram tool to avoid sending real messages
            with patch('tools.telegram_tool.send_telegram_message', new_callable=AsyncMock) as mock_send:
                from agents.scheduler_agent import SchedulerAgent
                scheduler = SchedulerAgent()
                
                # Manually trigger the process_due_messages method.
                await scheduler.process_due_messages()
                
                # Verify the Telegram tool was called with correct parameters
                mock_send.assert_called_once_with(parsed_command.target, parsed_command.message)
