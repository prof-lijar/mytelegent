from __future__ import annotations

import sqlite3
<<<<<<< HEAD
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional, Generator

from tools.config import Config
from schemas.models import ScheduledMessage, ParsedMessageCommand
<<<<<<< HEAD
<<<<<<< HEAD
=======
>>>>>>> backend/implement-scheduler

@contextmanager
def get_db_connection() -> Generator[sqlite3.Connection, None, None]:
    """Context manager for SQLite database connections."""
    Config.ensure_db_dir()
    conn = sqlite3.connect(Config.DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

def _row_to_scheduled_message(row: sqlite3.Row) -> ScheduledMessage:
    """Helper to convert a database row to a ScheduledMessage model."""
    return ScheduledMessage(
        id=row["id"],
        target=row["target"],
        target_type=row["target_type"],
        scheduled_time=datetime.fromisoformat(row["scheduled_time"]),
        message=row["message"],
        status=row["status"],
        retry_count=row["retry_count"],
        created_at=datetime.fromisoformat(row["created_at"]),
        sent_at=datetime.fromisoformat(row["sent_at"]) if row["sent_at"] else None,
        error_message=row["error_message"],
    )
<<<<<<< HEAD
=======
>>>>>>> backend/parsing-agent
=======
>>>>>>> backend/implement-scheduler

def initialize_database() -> None:
    """Initialize the SQLite database and create tables."""
    with get_db_connection() as conn:
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
            '''
        )
        conn.commit()

def insert_scheduled_message(parsed_command: ParsedMessageCommand) -> int:
    """Insert a scheduled message into the database."""
    with get_db_connection() as conn:
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
        conn.commit()
        return cursor.lastrowid

def get_due_messages(now: datetime) -> List[ScheduledMessage]:
    """Get messages that are due for sending."""
    with get_db_connection() as conn:
        cursor = conn.execute(
            '''
            SELECT id, target, target_type, scheduled_time, message, status, 
                   retry_count, created_at, sent_at, error_message 
            FROM scheduled_messages 
            WHERE status = 'pending' AND scheduled_time <= ?
            ''',
            (now.isoformat(),),
        )
        return [_row_to_scheduled_message(row) for row in cursor.fetchall()]

def mark_processing(message_id: int) -> None:
    """Mark a message as processing."""
    with get_db_connection() as conn:
        conn.execute(
            'UPDATE scheduled_messages SET status = ? WHERE id = ?',
            ('processing', message_id),
        )
        conn.commit()

def mark_sent(message_id: int) -> None:
    """Mark a message as sent."""
    with get_db_connection() as conn:
        conn.execute(
            'UPDATE scheduled_messages SET status = ?, sent_at = ? WHERE id = ?',
            ('sent', datetime.now(timezone.utc).isoformat(), message_id),
        )
        conn.commit()

def mark_failed(message_id: int, error: str) -> None:
    """Mark a message as failed."""
    with get_db_connection() as conn:
        conn.execute(
            'UPDATE scheduled_messages SET status = ?, error_message = ?, retry_count = retry_count + 1 WHERE id = ?',
            ('failed', error, message_id),
        )
        conn.commit()

def list_pending_messages() -> List[ScheduledMessage]:
    """List all pending messages."""
    with get_db_connection() as conn:
        cursor = conn.execute(
            '''
            SELECT id, target, target_type, scheduled_time, message, status, 
                   retry_count, created_at, sent_at, error_message 
            FROM scheduled_messages WHERE status = 'pending'
            ''',
        )
        return [_row_to_scheduled_message(row) for row in cursor.fetchall()]
=======
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
            cursor = conn.execute(
                '''
                SELECT id, target, target_type, scheduled_time, message, status, 
                       retry_count, created_at, sent_at, error_message 
                FROM scheduled_messages 
                WHERE status = 'pending' AND scheduled_time <= ?
                ''',
                (now.isoformat(),),
            )
            rows = cursor.fetchall()
            
            messages = []
            for row in rows:
                messages.append(
                    ScheduledMessage(
                        id=row[0],
                        target=row[1],
                        target_type=row[2],
                        scheduled_time=datetime.fromisoformat(row[3]),
                        message=row[4],
                        status=row[5],
                        retry_count=row[6],
                        created_at=datetime.fromisoformat(row[7]),
                        sent_at=datetime.fromisoformat(row[8]) if row[8] else None,
                        error_message=row[9],
                    )
                )
            return messages
    finally:
        conn.close()

def mark_processing(message_id: int) -> None:
    '''Mark a message as processing.'''
    conn = sqlite3.connect(Config.DB_PATH)
    try:
        with conn:
            conn.execute(
                'UPDATE scheduled_messages SET status = ? WHERE id = ?',
                ('processing', message_id),
            )
    finally:
        conn.close()

def mark_sent(message_id: int) -> None:
    '''Mark a message as sent.'''
    conn = sqlite3.connect(Config.DB_PATH)
    try:
        with conn:
            conn.execute(
                'UPDATE scheduled_messages SET status = ?, sent_at = ? WHERE id = ?',
                ('sent', datetime.now(timezone.utc).isoformat(), message_id),
            )
    finally:
        conn.close()

def mark_failed(message_id: int, error: str) -> None:
    '''Mark a message as failed.'''
    conn = sqlite3.connect(Config.DB_PATH)
    try:
        with conn:
            conn.execute(
                'UPDATE scheduled_messages SET status = ?, error_message = ?, retry_count = retry_count + 1 WHERE id = ?',
                ('failed', error, message_id),
            )
    finally:
        conn.close()

def list_pending_messages() -> List[ScheduledMessage]:
    '''List all pending messages.'''
    conn = sqlite3.connect(Config.DB_PATH)
    try:
        with conn:
            cursor = conn.execute(
                "SELECT id, target, target_type, scheduled_time, message, status, retry_count, created_at, sent_at, error_message FROM scheduled_messages WHERE status = 'pending'",
            )
            rows = cursor.fetchall()
            
            messages = []
            for row in rows:
                messages.append(
                    ScheduledMessage(
                        id=row[0],
                        target=row[1],
                        target_type=row[2],
                        scheduled_time=datetime.fromisoformat(row[3]),
                        message=row[4],
                        status=row[5],
                        retry_count=row[6],
                        created_at=datetime.fromisoformat(row[7]),
                        sent_at=datetime.fromisoformat(row[8]) if row[8] else None,
                        error_message=row[9],
                    )
                )
            return messages
    finally:
        conn.close()
>>>>>>> backend/telegram-tool
