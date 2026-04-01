from fastapi import WebSocket
from asyncpg import Connection


class ConnectionManager:
    def __init__(self):
        # Maps user_id -> WebSocket connection
        self.active_connections: dict[str, WebSocket] = {}

    async def connect(self, user_id: str, websocket: WebSocket) -> None:
        self.active_connections[user_id] = websocket

    def disconnect(self, user_id: str) -> None:
        self.active_connections.pop(user_id, None)

    async def send_to_user(self, user_id: str, message: dict) -> None:
        """
        Send a message to a specific user
        """

        websocket = self.active_connections.get(user_id)
        if websocket:
            await websocket.send_json(message)

    async def broadcast(self, message: dict) -> None:
        """
        Sends a message to ALL connected users
        """

        for websocket in self.active_connections.values():
            await websocket.send_json(message)

    def is_online(self, user_id: str) -> bool:
        return user_id in self.active_connections

# Single shared instance across your app
manager = ConnectionManager()