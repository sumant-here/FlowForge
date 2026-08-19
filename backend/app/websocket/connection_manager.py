import asyncio
import json
import logging
from typing import List, Set
from fastapi import WebSocket

logger = logging.getLogger("flowforge.ws")

class ConnectionManager:
    def __init__(self):
        self.active_connections: Set[WebSocket] = set()
        self._lock = asyncio.Lock()

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        async with self._lock:
            self.active_connections.add(websocket)
        logger.info(f"WebSocket client connected. Total clients: {len(self.active_connections)}")

    async def disconnect(self, websocket: WebSocket):
        async with self._lock:
            self.active_connections.discard(websocket)
        logger.info(f"WebSocket client disconnected. Total clients: {len(self.active_connections)}")

    async def broadcast(self, event_type: str, data: dict):
        message = json.dumps({"event": event_type, "data": data, "timestamp": asyncio.get_event_loop().time()})
        async with self._lock:
            dead_sockets = set()
            for connection in self.active_connections:
                try:
                    await connection.send_text(message)
                except Exception:
                    dead_sockets.add(connection)
            for dead in dead_sockets:
                self.active_connections.discard(dead)

ws_manager = ConnectionManager()
