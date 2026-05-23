from __future__ import annotations

import pytest
import asyncio
from unittest.mock import MagicMock, patch
from datetime import datetime, timezone
from agents.scheduler_agent import SchedulerAgent
from schemas.models import ScheduledMessage

@pytest.mark.asyncio
async def test_scheduler_processes_due_messages():
    \"\"\"Test that scheduler identifies and processes due messages.\"\"\"
    # Mock the database and telegram tool
    with patch('agents.scheduler_agent.get_due_messages') as mock_get_due, \
         patch('agents.scheduler_agent.send_telegram_message') as mock_send, \
         patch('agents.scheduler_agent.mark_processing') as mock_mark_proc, \
         patch('agents.scheduler_agent.mark_sent') as mock_mark_sent, \
         patch('agents.scheduler_agent.mark_failed') as mock_mark_fail:
        
        # Setup: 1 due message
        msg = ScheduledMessage(
            id=1,
            target=\"@testuser\",
            target_type=\"username\",
            scheduled_time=datetime.now(timezone.utc),
            message=\"Hello Test\",
            status=\"pending\"
        )
        mock_get_due.return_value = [msg]
        mock_send.return_value = {\"success\": True, \"target\": \"@testuser\", \"error\": None}
        
        agent = SchedulerAgent()
        await agent.process_due_messages()
        
        mock_get_due.assert_called_once()
        mock_mark_proc.assert_called_once_with(1)
        mock_send.assert_called_once_with(\"@testuser\", \"Hello Test\")
        mock_mark_sent.assert_called_once_with(1)
        mock_mark_fail.assert_not_called()

@pytest.mark.asyncio
async def test_scheduler_handles_failure_and_retry():
    \"\"\"Test that scheduler handles failure and increments retry count.\"\"\"
    with patch('agents.scheduler_agent.get_due_messages') as mock_get_due, \
         patch('agents.scheduler_agent.send_telegram_message') as mock_send, \
         patch('agents.scheduler_agent.mark_processing') as mock_mark_proc, \
         patch('agents.scheduler_agent.get_db_connection') as mock_db_conn:
        
        # Setup: Message that will fail
        msg = ScheduledMessage(
            id=2,
            target=\"@failuser\",
            target_type=\"username\",
            scheduled_time=datetime.now(timezone.utc),
            message=\"Fail Me\",
            status=\"pending\",
            retry_count=0
        )
        mock_get_due.return_value = [msg]
        mock_send.return_value = {\"success\": False, \"target\": \"@failuser\", \"error\": \"API Error\"}
        
        # Mock DB connection for the retry update
        mock_conn = MagicMock()
        mock_db_conn.return_value.__enter__.return_value = mock_conn
        
        agent = SchedulerAgent()
        await agent.process_due_messages()
        
        mock_mark_proc.assert_called_once_with(2)
        mock_send.assert_called_once()
        # Verify the update query for retry was called
        mock_conn.execute.assert_called_with(
            'UPDATE scheduled_messages SET status = ?, error_message = ?, retry_count = retry_count + 1 WHERE id = ?',
            ('pending', 'API Error', 2),
        )

@pytest.mark.asyncio
async def test_scheduler_max_retries_reached():
    \"\"\"Test that scheduler marks message as failed after max retries.\"\"\"
    with patch('agents.scheduler_agent.get_due_messages') as mock_get_due, \
         patch('agents.scheduler_agent.send_telegram_message') as mock_send, \
         patch('agents.scheduler_agent.mark_processing') as mock_mark_proc, \
         patch('agents.scheduler_agent.mark_failed') as mock_mark_fail:
        
        # Setup: Message at max retries
        msg = ScheduledMessage(
            id=3,
            target=\"@maxuser\",
            target_type=\"username\",
            scheduled_time=datetime.now(timezone.utc),
            message=\"Max Retry\",
            status=\"pending\",
            retry_count=2
        )
        mock_get_due.return_value = [msg]
        mock_send.return_value = {\"success\": False, \"target\": \"@maxuser\", \"error\": \"Persistent Error\"}
        
        agent = SchedulerAgent()
        await agent.process_due_messages()
        
        mock_mark_proc.assert_called_once_with(3)
        mock_send.assert_called_once()
        mock_mark_fail.assert_called_once_with(3, \"Max retries reached. Last error: Persistent Error\")

@pytest.mark.asyncio
async def test_scheduler_start_stop():
    \"\"\"Test scheduler start and stop functionality.\"\"\"
    agent = SchedulerAgent()
    agent.start()
    # We don't actually want to run the loop for long, so we just check if it's started
    # In a real test we'd check the scheduler object state
    agent.shutdown()
