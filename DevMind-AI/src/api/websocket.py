"""WebSocket endpoints for real-time updates."""
from __future__ import annotations

import asyncio
import json
from typing import Any, List
from fastapi import WebSocket, WebSocketDisconnect


class ConnectionManager:
    """Manages WebSocket connections."""

    def __init__(self):
        self.active_connections: dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, channel: str):
        """Accept and register a new connection."""
        await websocket.accept()
        if channel not in self.active_connections:
            self.active_connections[channel] = []
        self.active_connections[channel].append(websocket)

    def disconnect(self, websocket: WebSocket, channel: str):
        """Remove a connection."""
        if channel in self.active_connections:
            if websocket in self.active_connections[channel]:
                self.active_connections[channel].remove(websocket)
            if not self.active_connections[channel]:
                del self.active_connections[channel]

    async def broadcast(self, channel: str, message: dict):
        """Broadcast message to all connections in a channel."""
        if channel not in self.active_connections:
            return

        # Copy list to avoid modification during iteration if disconnect happens
        connections = self.active_connections[channel][:]
        for connection in connections:
            try:
                await connection.send_json(message)
            except Exception:
                # Disconnect dead connections
                self.disconnect(connection, channel)


manager = ConnectionManager()


async def websocket_endpoint(websocket: WebSocket, repo_id: str):
    """WebSocket endpoint for repo updates."""
    channel = f"repo:{repo_id}"
    await manager.connect(websocket, channel)

    try:
        while True:
            # Keep connection alive
            data = await websocket.receive_text()
            # Handle ping/pong or commands
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        manager.disconnect(websocket, channel)
    except Exception:
         # Handle other exceptions to ensure disconnect
        manager.disconnect(websocket, channel)


async def notify_scan_complete(repo_id: str, scan_type: str, results: dict):
    """Notify connected clients of scan completion."""
    await manager.broadcast(
        f"repo:{repo_id}",
        {
            "type": "scan_complete",
            "scan_type": scan_type,
            "results": results,
        },
    )


async def notify_review_complete(repo_id: str, pr_number: int, review: dict):
    """Notify connected clients of review completion."""
    await manager.broadcast(
        f"repo:{repo_id}",
        {
            "type": "review_complete",
            "pr_number": pr_number,
            "summary": review,
        },
    )
