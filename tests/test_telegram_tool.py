from __future__ import annotations

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from tools.telegram_tool import TelegramTool, send_telegram_message
from telethon import errors

@pytest.mark.asyncio
async def test_send_message_success():
    """Test successful message sending."""
    with patch("tools.telegram_tool.TelegramTool.get_client", new_callable=AsyncMock) as mock_get_client:
        mock_client = AsyncMock()
        mock_get_client.return_value = mock_client
        
        # Mock the delay to speed up tests
        with patch("asyncio.sleep", new_callable=AsyncMock):
            result = await send_telegram_message("test_user", "hello")
            
        assert result["success"] is True
        assert result["target"] == "test_user"
        mock_client.send_message.assert_called_once_with("test_user", "hello")

@pytest.mark.asyncio
async def test_send_message_flood_wait():
    """Test handling of FloodWaitError."""
    with patch("tools.telegram_tool.TelegramTool.get_client", new_callable=AsyncMock) as mock_get_client:
        mock_client = AsyncMock()
        mock_client.send_message.side_effect = errors.FloodWaitError(10)
        mock_get_client.return_value = mock_client
        
        with patch("asyncio.sleep", new_callable=AsyncMock):
            result = await send_telegram_message("test_user", "hello")
            
        assert result["success"] is False
        assert "FloodWait" in result["error"]

@pytest.mark.asyncio
async def test_send_message_generic_error():
    """Test handling of generic Telegram errors."""
    with patch("tools.telegram_tool.TelegramTool.get_client", new_callable=AsyncMock) as mock_get_client:
        mock_client = AsyncMock()
        mock_client.send_message.side_effect = Exception("Generic Error")
        mock_get_client.return_value = mock_client
        
        with patch("asyncio.sleep", new_callable=AsyncMock):
            result = await send_telegram_message("test_user", "hello")
            
        assert result["success"] is False
        assert result["error"] == "Generic Error"

@pytest.mark.asyncio
async def test_is_authorized_success():
    """Test authorization check success."""
    with patch("tools.telegram_tool.TelegramTool.get_client", new_callable=AsyncMock) as mock_get_client:
        mock_client = AsyncMock()
        mock_get_client.return_value = mock_client
        
        tool = TelegramTool()
        authorized = await tool.is_authorized()
        
        assert authorized is True
        mock_client.get_me.assert_called_once()

@pytest.mark.asyncio
async def test_is_authorized_failure():
    """Test authorization check failure."""
    with patch("tools.telegram_tool.TelegramTool.get_client", new_callable=AsyncMock) as mock_get_client:
        mock_client = AsyncMock()
        mock_client.get_me.side_effect = Exception("Auth failed")
        mock_get_client.return_value = mock_client
        
        tool = TelegramTool()
        authorized = await tool.is_authorized()
        
        assert authorized is False
