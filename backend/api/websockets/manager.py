import asyncio
from fastapi import WebSocket
from typing import Dict, List
import logging

logger = logging.getLogger(__name__)

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, job_id: str):
        await websocket.accept()
        if job_id not in self.active_connections:
            self.active_connections[job_id] = []
        self.active_connections[job_id].append(websocket)
        logger.info(f"WebSocket client connected to job {job_id}")

    def disconnect(self, websocket: WebSocket, job_id: str):
        if job_id in self.active_connections:
            try:
                self.active_connections[job_id].remove(websocket)
                if not self.active_connections[job_id]:
                    del self.active_connections[job_id]
                logger.info(f"WebSocket client disconnected from job {job_id}")
            except ValueError:
                pass

    async def broadcast_job_event(self, job_id: str, event_data: dict):
        if job_id in self.active_connections:
            disconnected_clients = []
            for connection in self.active_connections[job_id]:
                try:
                    await connection.send_json(event_data)
                except Exception as e:
                    logger.warning(f"Error sending to websocket: {e}")
                    disconnected_clients.append(connection)
            
            for client in disconnected_clients:
                self.disconnect(client, job_id)

manager = ConnectionManager()
