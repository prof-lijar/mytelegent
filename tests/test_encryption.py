from __future__ import annotations

import os
import sqlite3
import pytest
from pathlib import Path
from cryptography.fernet import Fernet
from tools.config import Config
from tools.encryption_tool import EncryptionTool
from tools.db_tool import initialize_database, insert_scheduled_message, get_db_connection
from schemas.models import ParsedMessageCommand
from datetime import datetime, timezone

# Use a separate database for testing
TEST_DB_PATH = "database/test_encryption.db"
Config.DB_PATH = TEST_DB_PATH

# Generate a valid Fernet key for testing
TEST_SECRET_KEY = Fernet.generate_key().decode()
Config.SECRET_KEY = TEST_SECRET_KEY

def setup_module():
    """Ensure the test database is fresh and Config.SECRET_KEY is set."""
    if Path(TEST_DB_PATH).exists():
        os.remove(TEST_DB_PATH)
    initialize_database()

def teardown_module():
    """Clean up the test database."""
    if Path(TEST_DB_PATH).exists():
        os.remove(TEST_DB_PATH)

def test_encryption_decryption():
    """Test that the EncryptionTool correctly encrypts and decrypts text."""
    original_text = "Hello, this is a secret message!"
    encrypted = EncryptionTool.encrypt(original_text)
    assert encrypted != original_text
    
    decrypted = EncryptionTool.decrypt(encrypted)
    assert decrypted == original_text

def test_db_encryption_storage():
    """Test that messages are stored encrypted in the database and decrypted when retrieved."""
    msg_text = "Secret Database Message"
    cmd = ParsedMessageCommand(
        target="test_user",
        target_type="username",
        scheduled_time=datetime.now(timezone.utc),
        message=msg_text,
        confidence=1.0
    )
    
    msg_id = insert_scheduled_message(cmd)
    
    # Manually check the database to ensure it is encrypted
    conn = get_db_connection()
    row = conn.execute("SELECT message FROM scheduled_messages WHERE id = ?", (msg_id,)).fetchone()
    conn.close()
    
    stored_message = row[0]
    assert stored_message != msg_text, "Message should be stored encrypted in the DB"
    
    # Verify it can be decrypted (via the tool)
    decrypted_message = EncryptionTool.decrypt(stored_message)
    assert decrypted_message == msg_text

def test_invalid_key_error():
    """Test that an invalid key raises a ValueError."""
    # Temporarily change the key to something invalid
    original_key = Config.SECRET_KEY
    Config.SECRET_KEY = "invalid-key"
    
    # We need to reset the internal _fernet cache in EncryptionTool to force re-initialization
    EncryptionTool._fernet = None
    
    try:
        with pytest.raises(ValueError):
            EncryptionTool.encrypt("test")
    finally:
        Config.SECRET_KEY = original_key
        EncryptionTool._fernet = None # Reset again
