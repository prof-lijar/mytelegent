from __future__ import annotations

import os
import sqlite3
import pytest
from datetime import datetime, timezone
from tools.config import Config
from tools.db_tool import initialize_database, insert_scheduled_message, list_pending_messages
from schemas.models import ParsedMessageCommand

@pytest.fixture(autouse=True)
def setup_encryption_test(monkeypatch):
    from cryptography.fernet import Fernet
    key = Fernet.generate_key().decode()
    monkeypatch.setattr(Config, "SECRET_KEY", key)
    monkeypatch.setattr(Config, "DB_PATH", "database/test_encryption.db")
    initialize_database()
    yield
    if os.path.exists(Config.DB_PATH):
        try:
            os.remove(Config.DB_PATH)
        except OSError:
            pass

def test_message_encryption_in_db():
    test_message = "Hello, this is a secret message!"
    cmd = ParsedMessageCommand(
        target="test_user",
        target_type="username",
        scheduled_time=datetime.now(timezone.utc),
        message=test_message,
        confidence=1.0
    )
    msg_id = insert_scheduled_message(cmd)
    conn = sqlite3.connect(Config.DB_PATH)
    cursor = conn.execute("SELECT message FROM scheduled_messages WHERE id = ?", (msg_id,))
    raw_message = cursor.fetchone()[0]
    conn.close()
    assert raw_message != test_message
    assert raw_message is not None
    pending = list_pending_messages()
    assert len(pending) == 1
    assert pending[0].message == test_message

def test_decryption_backward_compatibility():
    conn = sqlite3.connect(Config.DB_PATH)
    conn.execute(
        "INSERT INTO scheduled_messages (target, target_type, scheduled_time, message, status, created_at) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        ("old_user", "username", datetime.now(timezone.utc).isoformat(), "I am plain text", "pending", datetime.now(timezone.utc).isoformat())
    )
    conn.commit()
    conn.close()
    pending = list_pending_messages()
    assert len(pending) == 1
    assert pending[0].message == "I am plain text"
