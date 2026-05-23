from __future__ import annotations

import pytest
import asyncio
from unittest.mock import patch, MagicMock, AsyncMock
from main import main
from agents.scheduler_agent import SchedulerAgent
from schemas.models import ParsedMessageCommand, ScheduledMessage
from datetime import datetime, timezone

@pytest.mark.asyncio
async def test_full_system_e2e_flow():
    # End-to-End Validation Test:
    # 1. CLI Input -> Parsing -> Confirmation -> DB Storage
    # the scheduler agent uses ScheduledMessage objects, not dicts.
    
    # --- Setup Mocks ---
    test_command = "Tell Jisoo tomorrow at 9 AM that I finished the report"
    test_parsed = ParsedMessageCommand(
        target="Jisoo",
        target_type="username",
        message="I finished the report",
        scheduled_time=datetime(2026, 5, 24, 9, 0, tzinfo=timezone.utc),
        confidence=0.95
    )
    
    # Mock inputs: 1. The command, 2. Confirmation 'y', 3. 'exit' to break the loop
    input_values = [test_command, 'y', 'exit']
    
    with patch('builtins.input', side_effect=input_values), \
         patch('main.initialize_database'), \
         patch('main.ParsingAgent.parse_command', return_value=test_parsed), \
         patch('main.insert_scheduled_message', return_value=123) as mock_insert, \
         patch('tools.telegram_tool.send_telegram_message', new_callable=AsyncMock) as mock_send:
        
        # 1. Test CLI Flow
        main()
        
        # Verify parsing and storage were triggered
        mock_insert.assert_called_once_with(test_parsed)
        
        # 2. Test Scheduler Flow
        scheduler = SchedulerAgent()
        
        # Mock the DB fetch to return a list of ScheduledMessage objects
        test_msg = ScheduledMessage(
            id=123,
            target="Jisoo",
            target_type="username",
            message="I finished the report",
            scheduled_time=datetime(2026, 5, 23, 22, 0, tzinfo=timezone.utc),
            status="pending",
            retry_count=0
        )
        
        with patch('agents.scheduler_agent.get_due_messages', return_value=[test_msg]):
            await scheduler.process_due_messages()
            
            # Verify the telegram tool was called with correct parameters
            mock_send.assert_called_once_with('Jisoo', 'I finished the report')

if __name__ == "__main__":
    asyncio.run(test_full_system_e2e_flow())
