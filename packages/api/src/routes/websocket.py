"""WebSocket endpoints for real-time updates"""

import json
import logging

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from fastapi.websockets import WebSocketState

logger = logging.getLogger(__name__)

router = APIRouter()


# Store active connections by user_id
class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[str, set[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, user_id: str):
        await websocket.accept()
        if user_id not in self.active_connections:
            self.active_connections[user_id] = set()
        self.active_connections[user_id].add(websocket)
        logger.info(f'WebSocket connected for user {user_id}')

    def disconnect(self, websocket: WebSocket, user_id: str):
        if user_id in self.active_connections:
            self.active_connections[user_id].discard(websocket)
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
        logger.info(f'WebSocket disconnected for user {user_id}')

    async def send_personal_message(self, message: dict, user_id: str):
        if user_id in self.active_connections:
            # Create a copy of the set to avoid modification during iteration
            connections = self.active_connections[user_id].copy()
            for connection in connections:
                try:
                    if connection.client_state == WebSocketState.CONNECTED:
                        await connection.send_text(json.dumps(message))
                except Exception as e:
                    logger.error(f'Error sending message to user {user_id}: {e}')
                    # Remove the failed connection
                    self.active_connections[user_id].discard(connection)

    async def broadcast(self, message: dict):
        for user_id, _ in self.active_connections.items():
            await self.send_personal_message(message, user_id)


manager = ConnectionManager()


@router.websocket('/ws/recommendations/{user_id}')
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    await manager.connect(websocket, user_id)
    try:
        while True:
            # Keep the connection alive and handle any incoming messages
            data = await websocket.receive_text()
            # Echo back any received data (optional)
            await websocket.send_text(f'Echo: {data}')
    except WebSocketDisconnect:
        manager.disconnect(websocket, user_id)
    except Exception as e:
        logger.error(f'WebSocket error for user {user_id}: {e}')
        manager.disconnect(websocket, user_id)


# Function to notify when recommendations are ready
async def notify_recommendations_ready(user_id: str, recommendations: dict):
    """Notify a user when their personalized recommendations are ready"""
    message = {
        'type': 'recommendations_ready',
        'user_id': user_id,
        'recommendations': recommendations,
        'timestamp': recommendations.get('generated_at'),
    }
    await manager.send_personal_message(message, user_id)
