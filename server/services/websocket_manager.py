from fastapi import WebSocket
from asyncpg import Connection
from uuid import UUID


class ConnectionManager:
    def __init__(self):
        # Maps user_id -> WebSocket connection
        self.active_connections: dict[UUID, WebSocket] = {}

    async def connect(self, user_id: UUID, websocket: WebSocket) -> None:
        self.active_connections[user_id] = websocket

    def disconnect(self, user_id: UUID) -> None:
        self.active_connections.pop(user_id, None)

    async def send_to_user(self, user_id: UUID, websocket_payload: dict) -> None:
        """
        Send a message to a specific user.
        websocket_payload is the message to be sent, and is expected to be a dict of only string value.
        """

        websocket = self.active_connections.get(user_id)
        if websocket:
            await websocket.send_json(websocket_payload)

    async def broadcast(self, message: dict) -> None:
        """
        Sends a message to ALL connected users
        """

        for websocket in self.active_connections.values():
            await websocket.send_json(message)

    def is_online(self, user_id: UUID) -> bool:
        return user_id in self.active_connections

# Single shared instance across your app
manager = ConnectionManager()