from __future__ import annotations

import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime, timezone, timedelta
from agents.scheduler_agent import SchedulerAgent
from schemas.models import ScheduledMessage

@pytest.fixture
def mock_db_tool():
    with patch('agents.scheduler_agent.get_due_messages') as mock:
        yield mock

@pytest.fixture
def mock_telegram_tool():
    with patch('agents.scheduler_agent.send_telegram_message') as mock:
        yield mock

@pytest.fixture
def mock_db_actions():
    with patch('agents.scheduler_agent.mark_processing') as mock_proc, \
         patch('agents.scheduler_agent.mark_sent') as mock_sent, \
         patch('agents.scheduler_agent.mark_failed') as mock_fail, \
         patch('agents.scheduler_agent.mark_retry') as mock_retry:
        yield {
            'processing': mock_proc,
            'sent': mock_sent,
            'failed': mock_fail,
            'retry': mock_retry
        }

@pytest.mark.asyncio
async def test_process_due_messages_empty(mock_db_tool, mock_telegram_tool):
    # Setup: No messages due
    mock_db_tool.return_value = []
    
    agent = SchedulerAgent()
    await agent.process_due_messages()
    
    # Verify: Telegram tool should not be called
    mock_telegram_tool.assert_not_called()

@pytest.mark.asyncio
async def test_process_due_messages_success(mock_db_tool, mock_db_actions, mock_telegram_tool):
    # Setup: One message due
    msg = ScheduledMessage(
        id=1,
        target="test_user",
        target_type="username",
        scheduled_time=datetime.now(timezone.utc),
        message="Hello World",
        status="pending"
    )
    mock_db_tool.return_value = [msg]
    mock_telegram_tool.return_value = {"success": True, "target": "test_user", "error": None}
    
    agent = SchedulerAgent()
    await agent.process_due_messages()
    
    # Verify: Correct flow
    mock_db_actions['processing'].assert_called_once_with(1)
    mock_telegram_tool.assert_called_once_with("test_user", "Hello World")
    mock_db_actions['sent'].assert_called_once_with(1)

@pytest.mark.asyncio
async def test_process_due_messages_retry(mock_db_tool, mock_db_actions, mock_telegram_tool):
    # Setup: One message due with retry count 0
    msg = ScheduledMessage(
        id=1,
        target="test_user",
        target_type="username",
        scheduled_time=datetime.now(timezone.utc),
        message="Hello World",
        status="pending",
        retry_count=0
    )
    mock_db_tool.return_value = [msg]
    mock_telegram_tool.return_value = {"success": False, "target": "test_user", "error": "FloodWait"}
    
    agent = SchedulerAgent()
    await agent.process_due_messages()
    
    # Verify: Should mark for retry
    mock_db_actions['processing'].assert_called_once_with(1)
    mock_db_actions['retry'].assert_called_once_with(1, "FloodWait")
    mock_db_actions['sent'].assert_not_called()

@pytest.mark.asyncio
async def test_process_due_messages_max_retries(mock_db_tool, mock_db_actions, mock_telegram_tool):
    # Setup: One message due with retry count 2 (max)
    msg = ScheduledMessage(
        id=2,
        target="test_user",
        target_type="username",
        scheduled_time=datetime.now(timezone.utc),
        message="Hello World",
        status="pending",
        retry_count=2
    )
    mock_db_tool.return_value = [msg]
    mock_telegram_tool.return_value = {"success": False, "target": "test_user", "error": "Network Error"}
    
    agent = SchedulerAgent()
    await agent.process_due_messages()
    
    # Verify: Should mark as permanently failed
    mock_db_actions['processing'].assert_called_once_with(2)
    mock_db_actions['failed'].assert_called_once_with(2, "Max retries reached. Last error: Network Error")

@pytest.mark.asyncio
async def test_scheduler_start_stop(mock_db_tool):
    # This tests the scheduler's configuration, not the loop
    agent = SchedulerAgent()
    agent.start()
    # We don't need to actually wait for the loop, just verifying it doesn't crash on start
    agent.shutdown()
