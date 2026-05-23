from __future__ import annotations

import pytest
import asyncio
import sqlite3
from unittest.mock import patch, MagicMock, AsyncMock
from datetime import datetime, timedelta, timezone

from main import main
from tools.db_tool import initialize_database, get_scheduled_messages
from agents.scheduler_agent import SchedulerAgent
from tools.telegram_tool import send_telegram_message

# Use a temporary database for E2E tests
TEST_DB_PATH = "database/test_messages.db"

@pytest.fixture(autouse=True)
def setup_test_db():
    import tools.db_tool
    # Patch the database path in db_tool
    with patch('tools.db_tool.DB_PATH', TEST_DB_PATH):
        initialize_database()
        yield
        # Clean up
        import os
        if os.path.exists(TEST_DB_PATH):
            os.remove(TEST_DB_PATH)

@pytest.mark.asyncio
async def test_full_system_e2e_flow():
    \"\"\"
    End-to-End Test Flow:
    1. User enters command in CLI.
    2. ParsingAgent parses it.
    3. User confirms.
    4. Message is stored in DB.
    5. SchedulerAgent picks it up and sends via TelegramTool.
    \"\"\"
    
    # 1. Mock inputs for main()
    # Command, then 'y' for confirmation, then 'exit' to stop the loop
    test_input = [
        \"Tell Alice tomorrow at 10 AM that the meeting is moved\",
        \"y\",
        \"exit\"
    ]
    
    # 2. Mock ParsingAgent.parse_command to return a predictable result
    # We avoid real LLM calls to keep the test deterministic and fast
    from schemas.models import ParsedMessageCommand
    mock_parsed = ParsedMessageCommand(
        target=\"Alice\",
        target_type=\"username\",
        message=\"the meeting is moved\",
        scheduled_time=datetime.now(timezone.utc) + timedelta(days=1),
        confidence=0.99
    )
    
    # 3. Mocks for external services
    with patch('builtins.input', side_effect=test_input), \
         patch('agents.parsing_agent.ParsingAgent.parse_command', return_value=mock_parsed), \
         patch('tools.db_tool.DB_PATH', TEST_DB_PATH), \
         patch('tools.telegram_tool.TelegramClient') as mock_tg_client_class:
        
        # Setup Telegram mock
        mock_tg_client = AsyncMock()
        mock_tg_client_class.return_value.__aenter__.return_value = mock_tg_client
        
        # Run the CLI main loop
        # It should process the command, save it, and then exit
        main()
        
        # Verify: Message was stored in DB
        messages = get_scheduled_messages()
        assert len(messages) == 1
        assert messages[0]['target'] == \"Alice\"
        assert messages[0]['message'] == \"the meeting is moved\"
        
        # 4. Verify SchedulerAgent triggers the send
        # We'll manually trigger the scheduler's process_due_messages 
        # and mock the time to make the message "due"
        
        # Update the message in DB to be in the past so it's due
        conn = sqlite3.connect(TEST_DB_PATH)
        conn.execute(\"UPDATE scheduled_messages SET scheduled_time = ? WHERE id = 1\", 
                     (datetime.now(timezone.utc) - timedelta(minutes=1).isoformat(),))
        conn.commit()
        conn.close()
        
        scheduler = SchedulerAgent()
        # Mock the send_telegram_message tool to verify it's called
        with patch('agents.scheduler_agent.send_telegram_message', new_callable=AsyncMock) as mock_send:
            mock_send.return_value = {\"success\": True, \"target\": \"Alice\", \"error\": None}
            
            await scheduler.process_due_messages()
            
            # Verify Telegram tool was called with correct params
            mock_send.assert_called_once_with(\"Alice\", \"the meeting is moved\")
            
            # Verify status was updated to 'sent'
            conn = sqlite3.connect(TEST_DB_PATH)
            cursor = conn.cursor()
            cursor.execute(\"SELECT status FROM scheduled_messages WHERE id = 1\")
            status = cursor.fetchone()[0]
            conn.close()
            assert status == 'sent'

if __name__ == \"__main__\":
    # This allows running the file directly with pytest
    import pytest
    pytest.main([__file__])
