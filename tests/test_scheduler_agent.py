from __future__ import annotations

import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from datetime import datetime, timezone, timedelta
from agents.scheduler_agent import SchedulerAgent
from schemas.models import ScheduledMessage

@pytest.fixture
def mock_db_tool():
    with patch('agents.scheduler_agent.db_tool') as mock:
        yield mock

@pytest.fixture
def mock_telegram_tool():
    with patch('agents.scheduler_agent.telegram_tool') as mock:
        yield mock

@pytest.fixture
def scheduler_agent():
    return SchedulerAgent(check_interval=10)

@pytest.mark.asyncio
async def test_check_and_send_messages_no_due(scheduler_agent, mock_db_tool, mock_telegram_tool):
    \"\"\"Test that nothing happens if there are no due messages.\"\"\"
    mock_db_tool.get_due_messages.return_value = []
    
    await scheduler_agent.check_and_send_messages()
    
    mock_telegram_tool.send_telegram_message.assert_not_called()
    mock_db_tool.mark_processing.assert_not_called()

@pytest.mark.asyncio
async def test_check_and_send_messages_success(scheduler_agent, mock_db_tool, mock_telegram_tool):
    \"\"\"Test successful message delivery.\"\"\"
    msg = ScheduledMessage(
        id=1,
        target=\"@testuser\",
        target_type=\"username\",
        scheduled_time=datetime.now(timezone.utc),
        message=\"Hello!\",
        status=\"pending\",
        retry_count=0,
        created_at=datetime.now(timezone.utc),
        sent_at=None,
        error_message=None
    )
    mock_db_tool.get_due_messages.return_value = [msg]
    mock_telegram_tool.send_telegram_message.return_value = {\"success\": True, \"target\": \"@testuser\", \"error\": None}
    
    await scheduler_agent.check_and_send_messages()
    
    mock_db_tool.mark_processing.assert_called_once_with(1)
    mock_telegram_tool.send_telegram_message.assert_called_once_with(\"@testuser\", \"Hello!\")
    mock_db_tool.mark_sent.assert_called_once_with(1)

@pytest.mark.asyncio
async def test_check_and_send_messages_retry(scheduler_agent, mock_db_tool, mock_telegram_tool):
    \"\"\"Test that a failed message is scheduled for retry if retry_count < 2.\"\"\"
    msg = ScheduledMessage(
        id=2,
        target=\"@testuser\",
        target_type=\"username\",
        scheduled_time=datetime.now(timezone.utc),
        message=\"Hello!\",
        status=\"pending\",
        retry_count=0,
        error_message=None,
        created_at=datetime.now(timezone.utc),
        sent_at=None
    )
    mock_db_tool.get_due_messages.return_value = [msg]
    mock_telegram_tool.send_telegram_message.return_value = {\"success\": False, \"target\": \"@testuser\", \"error\": \"Network Error\"}
    
    await scheduler_agent.check_and_send_messages()
    
    mock_db_tool.mark_processing.assert_called_once_with(2)
    mock_db_tool.mark_retry.assert_called_once_with(2, \"Network Error\")
    mock_db_tool.mark_sent.assert_not_called()

@pytest.mark.asyncio
async def test_check_and_send_messages_fail_permanent(scheduler_agent, mock_db_tool, mock_telegram_tool):
    \"\"\"Test that a message is marked failed after max retries (2).\"\"\"
    msg = ScheduledMessage(
        id=3,
        target=\"@testuser\",
        target_type=\"username\",
        scheduled_time=datetime.now(timezone.utc),
        message=\"Hello!\",
        status=\"pending\",
        retry_count=2,
        error_message=None,
        created_at=datetime.now(timezone.utc),
        sent_at=None
    )
    mock_db_tool.get_due_messages.return_value = [msg]
    mock_telegram_tool.send_telegram_message.return_value = {\"success\": False, \"target\": \"@testuser\", \"error\": \"Unauthorized\"}
    
    await scheduler_agent.check_and_send_messages()
    
    mock_db_tool.mark_processing.assert_called_once_with(3)
    mock_db_tool.mark_retry.assert_not_called()
    mock_db_tool.mark_failed.assert_called_once_with(3, \"Unauthorized\")

@pytest.mark.asyncio
async def test_check_and_send_messages_exception(scheduler_agent, mock_db_tool, mock_telegram_tool):
    \"\"\"Test that unexpected exceptions are handled and result in retry or failure.\"\"\"
    msg = ScheduledMessage(
        id=4,
        target=\"@testuser\",
        target_type=\"username\",
        # Fix: ensure scheduled_time is timezone aware
        scheduled_time=datetime.now(timezone.utc),
        message=\"Hello!\",
        status=\"pending\",
        retry_count=0,
        error_message=None,
        created_at=datetime.now(timezone.utc),
        sent_at=None
    )
    mock_db_tool.get_due_messages.return_value = [msg]
    # Force an exception during the send process
    mock_telegram_tool.send_telegram_message.side_effect = Exception(\"Critical failure\")
    
    await scheduler_agent.check_and_send_messages()
    
    mock_db_tool.mark_processing.assert_called_once_with(4)
    mock_db_tool.mark_retry.assert_called_once_with(4, \"Critical failure\")
