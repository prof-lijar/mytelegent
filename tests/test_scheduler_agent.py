import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timezone
from agents.scheduler_agent import SchedulerAgent
from schemas.models import ScheduledMessage

@pytest.mark.asyncio
async def test_scheduler_process_success():
    # Test that a due message is sent successfully and marked as sent.
    agent = SchedulerAgent()
    
    # Mock message
    msg = ScheduledMessage(
        id=1,
        target="@user",
        target_type="username",
        scheduled_time=datetime.now(timezone.utc),
        message="Hello",
        status="pending"
    )
    
    with patch("agents.scheduler_agent.mark_processing") as mock_mark_proc, \
         patch("agents.scheduler_agent.send_telegram_message", new_callable=AsyncMock) as mock_send, \
         patch("agents.scheduler_agent.mark_sent") as mock_mark_sent:
        
        mock_send.return_value = {"success": True, "target": "@user", "error": None}
        
        await agent._process_message(msg)
        
        mock_mark_proc.assert_called_once_with(1)
        mock_send.assert_called_once_with("@user", "Hello")
        mock_mark_sent.assert_called_once_with(1)

@pytest.mark.asyncio
async def test_scheduler_process_failure_retry():
    # Test that a failed message is retried if retry count is within limit.
    agent = SchedulerAgent(max_retries=2)
    
    msg = ScheduledMessage(
        id=1,
        target="@user",
        target_type="username",
        scheduled_time=datetime.now(timezone.utc),
        message="Hello",
        status="pending",
        retry_count=0
    )
    
    with patch("agents.scheduler_agent.mark_processing"), \
         patch("agents.scheduler_agent.send_telegram_message", new_callable=AsyncMock) as mock_send, \
         patch("agents.scheduler_agent.mark_failed") as mock_mark_failed, \
         patch("agents.scheduler_agent.get_message_by_id") as mock_get_msg, \
         patch("agents.scheduler_agent.update_message_status") as mock_update_status:
        
        mock_send.return_value = {"success": False, "target": "@user", "error": "API Error"}
        # Simulate that after mark_failed, retry_count became 1
        mock_get_msg.return_value = msg.model_copy(update={"retry_count": 1})
        
        await agent._process_message(msg)
        
        mock_mark_failed.assert_called_once_with(1, "API Error")
        mock_update_status.assert_called_once_with(1, "pending", error_message="API Error")

@pytest.mark.asyncio
async def test_scheduler_process_failure_max_retries():
    # Test that a message is marked as failed when max retries are reached.
    agent = SchedulerAgent(max_retries=2)
    
    msg = ScheduledMessage(
        id=1,
        target="@user",
        target_type="username",
        scheduled_time=datetime.now(timezone.utc),
        message="Hello",
        status="pending",
        retry_count=2
    )
    
    with patch("agents.scheduler_agent.mark_processing"), \
         patch("agents.scheduler_agent.send_telegram_message", new_callable=AsyncMock) as mock_send, \
         patch("agents.scheduler_agent.mark_failed") as mock_mark_failed, \
         patch("agents.scheduler_agent.get_message_by_id") as mock_get_msg, \
         patch("agents.scheduler_agent.update_message_status") as mock_update_status:
        
        mock_send.return_value = {"success": False, "target": "@user", "error": "API Error"}
        # Simulate that after mark_failed, retry_count became 3
        mock_get_msg.return_value = msg.model_copy(update={"retry_count": 3})
        
        await agent._process_message(msg)
        
        mock_mark_failed.assert_called_once_with(1, "API Error")
        # Should NOT be set back to pending
        mock_update_status.assert_not_called()

@pytest.mark.asyncio
async def test_scheduler_check_due_messages():
    # Test that the scheduler identifies due messages and processes them.
    agent = SchedulerAgent()
    
    msg = ScheduledMessage(
        id=1,
        target="@user",
        target_type="username",
        scheduled_time=datetime.now(timezone.utc),
        message="Hello",
        status="pending"
    )
    
    with patch("agents.scheduler_agent.get_due_messages") as mock_get_due, \
         patch("agents.scheduler_agent.SchedulerAgent._process_message", new_callable=AsyncMock) as mock_process:
        
        mock_get_due.return_value = [msg]
        
        await agent._check_due_messages()
        
        mock_process.assert_called_once_with(msg)
