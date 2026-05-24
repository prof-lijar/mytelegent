import pytest
import asyncio
import os
from unittest.mock import patch, AsyncMock
from datetime import datetime, timedelta, timezone
from main import main
from tools.db_tool import get_db_connection
from agents.scheduler_agent import SchedulerAgent
from schemas.models import ParsedMessageCommand

# Mock data
USER_INPUT = "Tell Jisoo tomorrow at 9 AM that I finished the report"
CONFIRMATION = "y"
EXIT_CMD = "exit"
MOCK_PARSED = ParsedMessageCommand(
    target="Jisoo",
    target_type="name",
    message="I finished the report",
    scheduled_time=datetime.now(timezone.utc) - timedelta(minutes=1), # Set in past to trigger scheduler
    confidence=0.95
)

@pytest.fixture(autouse=True)
def setup_e2e_db():
    # Use a separate test database for E2E
    os.environ["DATABASE_PATH"] = "database/test_e2e_messages.db"
    yield
    if os.path.exists("database/test_e2e_messages.db"):
        try:
            os.remove("database/test_e2e_messages.db")
        except OSError:
            pass

def test_e2e_flow():
    # 1. Mock inputs for the CLI loop: command -> confirmation -> exit
    inputs = [USER_INPUT, CONFIRMATION, EXIT_CMD]
    
    # 2. Mock the ParsingAgent to avoid LLM calls
    # 3. Mock the async send_telegram_message function
    # IMPORTANT: Patch where it is USED (agents.scheduler_agent), not where it is DEFINED (tools.telegram_tool)
    with patch('builtins.input', side_effect=inputs), \
         patch('agents.parsing_agent.ParsingAgent.parse_command', return_value=MOCK_PARSED), \
         patch('agents.scheduler_agent.send_telegram_message', new_callable=AsyncMock) as mock_send, \
         patch('tools.logging_tool.get_logger'):
        
        mock_send.return_value = {"success": True}
        
        # Run the main CLI
        main()
        
        # Verify: Message should be in the DB
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT target, message FROM scheduled_messages WHERE target=?", (MOCK_PARSED.target,))
        row = cursor.fetchone()
        conn.close()
        
        assert row is not None, "Message was not saved to the database"
        assert row[0] == "Jisoo"
        assert row[1] == "I finished the report"
        
        # 4. Verify the scheduler processing
        scheduler = SchedulerAgent()
        # Use asyncio.run to execute the async process_due_messages method
        asyncio.run(scheduler.process_due_messages())
        
        # Verify: Telegram tool should have been called
        assert mock_send.called, "Telegram tool was not called by the scheduler"
        
        # Check if the correct arguments were passed in any of the calls
        called_with_target = any(
            call.args[0] == "Jisoo" or (call.kwargs.get('target') == "Jisoo")
            for call in mock_send.call_args_list
        )
        called_with_msg = any(
            call.args[1] == "I finished the report" or (call.kwargs.get('message') == "I finished the report")
            for call in mock_send.call_args_list
        )
        
        assert called_with_target, "Target 'Jisoo' was not passed to send_telegram_message"
        assert called_with_msg, "Message 'I finished the report' was not passed to send_telegram_message"

if __name__ == "__main__":
    pytest.main([__file__])
