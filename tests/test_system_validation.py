import pytest
import asyncio
import os
import sys
from unittest.mock import patch, AsyncMock
from datetime import datetime, timedelta, timezone
from main import main
from tools.db_tool import get_db_connection, initialize_database
from agents.scheduler_agent import SchedulerAgent
from schemas.models import ParsedMessageCommand
from tools.config import Config

# Mock data
USER_INPUT = "Tell Alice tomorrow at 9 AM that I am coming"
CONFIRMATION = "y"
MOCK_PARSED = ParsedMessageCommand(
    target="Alice",
    target_type="name",
    message="I am coming",
    scheduled_time=datetime.now(timezone.utc) - timedelta(minutes=1), # Set in past to trigger scheduler
    confidence=0.95
)

@pytest.fixture(autouse=True)
def setup_validation_db():
    # Set environment variables for the test
    os.environ["SECRET_KEY"] = "test-val-secret-key-12345"
    os.environ["SQLITE_DB_PATH"] = "database/test_system_val.db"
    
    # Force reload Config to pick up environment variables
    with patch('tools.db_tool.Config.DB_PATH', 'database/test_system_val.db'), \
         patch('tools.db_tool.Config.SECRET_KEY', 'test-val-secret-key-12345'):
        initialize_database()
        yield
        if os.path.exists("database/test_system_val.db"):
            try:
                os.remove("database/test_system_val.db")
            except OSError:
                pass

def test_full_system_flow():
    # This test simulates the entire user journey
    
    # 1. Mock inputs for the confirmation flow
    inputs = [CONFIRMATION]
    
    # We use a list of arguments to simulate different CLI calls
    # Sequence: schedule -> list -> run-scheduler -> list -> schedule -> cancel -> list
    
    # --- STEP 1: Schedule a message ---
    test_argv_schedule = ["main.py", "schedule", USER_INPUT]
    with patch('sys.argv', test_argv_schedule), \
         patch('builtins.input', side_effect=inputs), \
         patch('agents.parsing_agent.ParsingAgent.parse_command', return_value=MOCK_PARSED), \
         patch('tools.logging_tool.get_logger'), \
         patch('tools.db_tool.Config.SECRET_KEY', 'test-val-secret-key-12345'), \
         patch('tools.db_tool.Config.DB_PATH', 'database/test_system_val.db'):
        main()

    # Verify it's in the DB as pending
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, status FROM scheduled_messages WHERE target='Alice'")
    row = cursor.fetchone()
    conn.close()
    assert row is not None, "Message should be scheduled"
    msg_id = row[0]
    assert row[1] == 'pending', "Status should be pending"

    # --- STEP 2: List messages ---
    test_argv_list = ["main.py", "list"]
    with patch('sys.argv', test_argv_list), \
         patch('tools.logging_tool.get_logger'), \
         patch('tools.db_tool.Config.SECRET_KEY', 'test-val-secret-key-12345'), \
         patch('tools.db_tool.Config.DB_PATH', 'database/test_system_val.db'):
        main() # Should execute without error

    # --- STEP 3: Run Scheduler ---
    with patch('agents.scheduler_agent.send_telegram_message', new_callable=AsyncMock) as mock_send, \
         patch('tools.logging_tool.get_logger'), \
         patch('tools.db_tool.Config.SECRET_KEY', 'test-val-secret-key-12345'), \
         patch('tools.db_tool.Config.DB_PATH', 'database/test_system_val.db'):
        mock_send.return_value = {"success": True}
        
        # Simulate: python main.py run-scheduler
        test_argv_run = ["main.py", "run-scheduler"]
        with patch('sys.argv', test_argv_run):
            # Call processing logic directly to simulate one cycle
            scheduler = SchedulerAgent()
            asyncio.run(scheduler.process_due_messages())

    # Verify status changed to 'sent'
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT status FROM scheduled_messages WHERE id=?", (msg_id,))
    row = cursor.fetchone()
    conn.close()
    assert row[0] == 'sent', "Status should be 'sent' after scheduler runs"

    # --- STEP 4: Schedule another and Cancel it ---
    inputs_cancel = [CONFIRMATION]
    test_argv_schedule_2 = ["main.py", "schedule", "Tell Bob I'm late"]
    MOCK_PARSED_2 = ParsedMessageCommand(
        target="Bob",
        target_type="name",
        message="I'm late",
        scheduled_time=datetime.now(timezone.utc) + timedelta(hours=1),
        confidence=0.95
    )
    
    with patch('sys.argv', test_argv_schedule_2), \
         patch('builtins.input', side_effect=inputs_cancel), \
         patch('agents.parsing_agent.ParsingAgent.parse_command', return_value=MOCK_PARSED_2), \
         patch('tools.logging_tool.get_logger'), \
         patch('tools.db_tool.Config.SECRET_KEY', 'test-val-secret-key-12345'), \
         patch('tools.db_tool.Config.DB_PATH', 'database/test_system_val.db'):
        main()

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM scheduled_messages WHERE target='Bob'")
    row = cursor.fetchone()
    conn.close()
    assert row is not None, "Message for Bob should be scheduled"
    bob_id = row[0]

    # Cancel the message
    test_argv_cancel = ["main.py", "cancel", str(bob_id)]
    with patch('sys.argv', test_argv_cancel), \
         patch('tools.logging_tool.get_logger'), \
         patch('tools.db_tool.Config.SECRET_KEY', 'test-val-secret-key-12345'), \
         patch('tools.db_tool.Config.DB_PATH', 'database/test_system_val.db'):
        main()

    # Verify status is 'cancelled'
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT status FROM scheduled_messages WHERE id=?", (bob_id,))
    row = cursor.fetchone()
    conn.close()
    assert row[0] == 'cancelled', f"Status should be 'cancelled' for ID {bob_id}"

if __name__ == "__main__":
    pytest.main([__file__])
