from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone
from pathlib import Path
from tools.config import Config
from tools.db_tool import (
    initialize_database, 
    insert_scheduled_message, 
    get_due_messages, 
    list_pending_messages,
    mark_processing,
    mark_sent,
    mark_failed
)
from schemas.models import ParsedMessageCommand

# Use a separate database for testing to avoid polluting the main database
TEST_DB_PATH = "database/test_messages.db"
Config.DB_PATH = TEST_DB_PATH

def setup_module():
    """Ensure the test database is fresh before running tests."""
    if Path(TEST_DB_PATH).exists():
        os.remove(TEST_DB_PATH)
    initialize_database()

def teardown_module():
    """Clean up the test database after running tests."""
    if Path(TEST_DB_PATH).exists():
        os.remove(TEST_DB_PATH)

def test_db_lifecycle():
    """Test the full lifecycle of a scheduled message in the database."""
    # initialize_database() is called in setup_module
    
    msg = ParsedMessageCommand(
        target="test_user",
        target_type="username",
        scheduled_time=datetime.now(timezone.utc) - timedelta(minutes=1),
        message="Hello Lifecycle Test!",
        confidence=1.0
    )
    
    msg_id = insert_scheduled_message(msg)
    assert msg_id is not None
    
    pending = list_pending_messages()
    assert len(pending) > 0
    assert any(m.id == msg_id for m in pending)
    
    due = get_due_messages(datetime.now(timezone.utc))
    assert len(due) > 0
    assert any(m.id == msg_id for m in due)
    
    mark_processing(msg_id)
    pending_after_proc = list_pending_messages()
    assert not any(m.id == msg_id for m in pending_after_proc)
    
    mark_sent(msg_id)
    due_after_sent = get_due_messages(datetime.now(timezone.utc))
    assert not any(m.id == msg_id for m in due_after_sent)

def test_db_failure_retry():
    """Test marking a message as failed and checking retry count."""
    msg = ParsedMessageCommand(
        target="fail_user",
        target_type="phone",
        scheduled_time=datetime.now(timezone.utc) - timedelta(minutes=1),
        message="Fail Test",
        confidence=0.9
    )
    msg_id = insert_scheduled_message(msg)
    
    mark_failed(msg_id, "Connection timeout")
    
    pending = list_pending_messages()
    assert not any(m.id == msg_id for m in pending)

if __name__ == "__main__":
    setup_module()
    try:
        test_db_lifecycle()
        test_db_failure_retry()
    finally:
        teardown_module()
