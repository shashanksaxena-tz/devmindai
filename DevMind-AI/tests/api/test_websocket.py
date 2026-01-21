import pytest
from unittest.mock import AsyncMock, MagicMock
from src.api.websocket import ConnectionManager, notify_scan_complete

@pytest.mark.asyncio
async def test_connection_manager():
    manager = ConnectionManager()
    mock_ws = AsyncMock()

    await manager.connect(mock_ws, "channel1")
    assert "channel1" in manager.active_connections
    assert len(manager.active_connections["channel1"]) == 1

    await manager.broadcast("channel1", {"test": "data"})
    mock_ws.send_json.assert_called_with({"test": "data"})

    manager.disconnect(mock_ws, "channel1")
    assert "channel1" not in manager.active_connections

@pytest.mark.asyncio
async def test_notify_scan_complete():
    # We need to patch the global manager in src.api.websocket
    from src.api.websocket import manager

    mock_ws = AsyncMock()
    await manager.connect(mock_ws, "repo:123")

    await notify_scan_complete("123", "security", {"issues": []})

    mock_ws.send_json.assert_called()
    call_args = mock_ws.send_json.call_args[0][0]
    assert call_args["type"] == "scan_complete"
    assert call_args["scan_type"] == "security"

    # cleanup
    manager.disconnect(mock_ws, "repo:123")
