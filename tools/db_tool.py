from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional

from tools.config import Config
from schemas.models import ScheduledMessage, ParsedMessageCommand

def initialize_database() -> None:
    '''Initialize the SQLite database and create tables.'''
    Config.ensure_db_dir()
    conn = sqlite3.connect(Config.DB_PATH)
    try:
        with conn:
            conn.execute(
                '''
                CREATE TABLE IF NOT EXISTS scheduled_messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    target TEXT NOT NULL,
                    target_type TEXT NOT NULL,
                    scheduled_time TEXT NOT NULL,
                    message TEXT NOT NULL,
                    status TEXT NOT NULL,
                    retry_count INTEGER DEFAULT 0,
                    created_at TEXT NOT NULL,
                    sent_at TEXT,
                    error_message TEXT
                )
                ''',
            )
    finally:
        conn.close()

def insert_scheduled_message(parsed_command: ParsedMessageCommand) -> int:
    '''Insert a scheduled message into the database.'''
    conn = sqlite3.connect(Config.DB_PATH)
    try:
        with conn:
            cursor = conn.execute(
                '''
                INSERT INTO scheduled_messages (
                    target, target_type, scheduled_time, message, status, created_at
                ) VALUES (?, ?, ?, ?, ?, ?)
                ''',
                (
                    parsed_command.target,
                    parsed_command.target_type,
                    parsed_command.scheduled_time.isoformat(),
                    parsed_command.message,
                    'pending',
                    datetime.now(timezone.utc).isoformat(),
                ),
            )
            return cursor.lastrowid
    finally:
        conn.close()

def get_due_messages(now: datetime) -> List[ScheduledMessage]:
    '''Get messages that are due for sending.'''
    conn = sqlite3.connect(Config.DB_PATH)
    try:
        with conn:
    try:
        with get_db_connection() as conn:
            cursor = conn.execute(
                '''
                SELECT id, target, target_type, scheduled_time, message, status, 
                       retry_count, created_at, sent_at, error_message 
=======
                FROM scheduled_messages WHERE status = 'pending'
                ''',
            )
            return [_row_to_scheduled_message(row) for row in cursor.fetchall()]
    except Exception as e:
        logger.error(f"Failed to list pending messages: {e}", exc_info=True)
        raise
>>>>>>> backend/cli-and-logging
