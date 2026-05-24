from __future__ import annotations

import os
import sqlite3
import pytest
from datetime import datetime, timezone
from tools.config import Config
from tools.db_tool import initialize_database, insert_scheduled_message, get_due_messages, list_pending_messages
from schemas.models import ParsedMessageCommand

# Mock environment variable for tests
os.environ["SECRET_KEY"] = "test-secret-key-12345"
os.environ["SQLITE_DB_PATH"] = "tests/test_messages.db"

@pytest.fixture(scope="module", autouse=True)
def setup_db():
    initialize_database()
    yield
    if os.path.exists("tests/test_messages.db"):
        os.remove("tests/test_messages.db")

def test_encryption_decryption_cycle():
    """Test that messages are encrypted in DB and decrypted on retrieval."""
    command = ParsedMessageCommand(
        target="test_user",
        target_type="username",
        scheduled_time=datetime.now(timezone.utc),
        message="Hello, this is a secret message!",
        confidence=1.0
    )
    
    msg_id = insert_scheduled_message(command)
    
    # Verify encryption in DB (manual check)
    conn = sqlite3.connect(Config.DB_PATH)
    cursor = conn.execute("SELECT message FROM scheduled_messages WHERE id = ?", (msg_id,))
    encrypted_val = cursor.fetchone()[0]
    conn.close()
    
    assert encrypted_val != "Hello, this is a secret message!"
    assert encrypted_val is not None
    
    # Verify decryption on retrieval
    pending = list_pending_messages()
    assert len(pending) > 0
    assert pending[0].message == "Hello, this is a secret message!"

def test_get_due_messages_decryption():
    """Test that due messages are also decrypted."""
    # Create a message that is already due
    past_time = datetime(2020, 1, 1, tzinfo=timezone.utc)
    command = ParsedMessageCommand(
        target="past_user",
        target_type="username",
        scheduled_time=past_time,
        message="Past secret message",
        confidence=1.0
    )
    insert_scheduled_message(command)
    
    due = get_due_messages(datetime.now(timezone.utc))
    assert any(m.message == "Past secret message" for m in due)
