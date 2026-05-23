from __future__ import annotations

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from tools.telegram_tool import send_telegram_message
from telethon import errors

@pytest.mark.asyncio
async def test_send_message_success():
    """Test successful message sending."""
    # Mock TelegramClient context manager
    with patch('tools.telegram_tool.TelegramClient') as mock_client_class:
        mock_client = AsyncMock()
        mock_client_class.return_value.__aenter__.return_value = mock_client
        
        # Mock the delay to speed up tests
        with patch('asyncio.sleep', new_callable=AsyncMock):
            # Mock Config validation to avoid needing real env vars
            with patch('tools.telegram_tool.Config.validate_telegram_config'):
                result = await send_telegram_message("test_user", "hello")
            
        assert result["success"] is True
        assert result["target"] == "test_user"
        mock_client.send_message.assert_called_once_with("test_user", "hello")

@pytest.mark.asyncio
async def test_send_message_invalid_user():
    """Test handling of UserIdInvalidError."""
    with patch('tools.telegram_tool.TelegramClient') as mock_client_class:
        mock_client = AsyncMock()
        # Use the errors.api path as seen in tools/telegram_tool.py
        mock_client.send_message.side_effect = errors.api.UserIdInvalidError("Invalid user")
        mock_client_class.return_value.__aenter__.return_value = mock_client
        
        with patch('asyncio.sleep', new_callable=AsyncMock):
            with patch('tools.telegram_tool.Config.validate_telegram_config'):
                result = await send_telegram_message("invalid_user", "hello")
            
        assert result["success"] is False
        assert "Invalid user ID or username" in result["error"]

@pytest.mark.asyncio
async def test_send_message_generic_error():
    """Test handling of generic Telegram errors."""
    with patch('tools.telegram_tool.TelegramClient') as mock_client_class:
        mock_client = AsyncMock()
        mock_client.send_message.side_effect = Exception("Generic Error")
        mock_client_class.return_value.__aenter__.return_value = mock_client
        
        with patch('asyncio.sleep', new_callable=AsyncMock):
            with patch('tools.telegram_tool.Config.validate_telegram_config'):
                result = await send_telegram_message("test_user", "hello")
            
        assert result["success"] is False
        assert "Unexpected error" in result["error"]
