"""
WebSocket handler for real-time chat interface
"""

import json
import logging
from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, Set

from backend.services.executor_service import ExecutorService, get_executor_service
from backend.services.auth import verify_api_key

logger = logging.getLogger("skill_executor.websocket")


class ConnectionManager:
    """Manage WebSocket connections"""

    def __init__(self):
        self.active_connections: Set[WebSocket] = set()

    async def connect(self, websocket: WebSocket) -> None:
        """Accept and register a new connection"""
        await websocket.accept()
        self.active_connections.add(websocket)
        logger.info(f"WebSocket connected. Total connections: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket) -> None:
        """Remove a connection"""
        self.active_connections.discard(websocket)
        logger.info(f"WebSocket disconnected. Total connections: {len(self.active_connections)}")

    async def send_message(self, message: str | dict, websocket: WebSocket) -> None:
        """Send a message to a specific connection"""
        if isinstance(message, dict):
            message = json.dumps(message)

        await websocket.send_text(message)

    async def broadcast(self, message: str | dict) -> None:
        """Broadcast a message to all active connections"""
        if isinstance(message, dict):
            message = json.dumps(message)

        disconnected = set()
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception as e:
                logger.error(f"Error broadcasting to connection: {e}")
                disconnected.add(connection)

        # Remove disconnected clients
        for connection in disconnected:
            self.disconnect(connection)


# Global connection manager
manager = ConnectionManager()


async def chat_websocket(websocket: WebSocket) -> None:
    """
    WebSocket endpoint for real-time chat interface

    Client should send messages in JSON format:
    {
        "type": "execute",
        "query": "user's question here"
    }

    Server responds with:
    {
        "type": "chunk" | "done" | "error",
        "content": "response content"
    }
    """
    # Get executor service instance
    executor = get_executor_service()
    await manager.connect(websocket)

    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()

            try:
                message = json.loads(data)
            except json.JSONDecodeError:
                await manager.send_message({
                    "type": "error",
                    "content": "Invalid JSON format"
                }, websocket)
                continue

            msg_type = message.get("type")

            if msg_type == "execute":
                # Stream execution results
                query = message.get("query", "")
                if not query:
                    await manager.send_message({
                        "type": "error",
                        "content": "Query is required"
                    }, websocket)
                    continue

                try:
                    async for chunk in executor.stream_execute(query):
                        await manager.send_message({
                            "type": "chunk",
                            "content": chunk
                        }, websocket)

                    # Send completion message
                    await manager.send_message({
                        "type": "done",
                        "content": None
                    }, websocket)

                except Exception as e:
                    logger.error(f"Error executing query: {e}", exc_info=True)
                    await manager.send_message({
                        "type": "error",
                        "content": f"Execution failed: {str(e)}"
                    }, websocket)

            elif msg_type == "ping":
                # Heartbeat/ping
                await manager.send_message({
                    "type": "pong",
                    "content": None
                }, websocket)

            else:
                await manager.send_message({
                    "type": "error",
                    "content": f"Unknown message type: {msg_type}"
                }, websocket)

    except WebSocketDisconnect:
        manager.disconnect(websocket)
        logger.info("WebSocket client disconnected normally")

    except Exception as e:
        logger.error(f"WebSocket error: {e}", exc_info=True)
        manager.disconnect(websocket)
