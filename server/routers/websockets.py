from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from asyncpg import Connection

from server.services.websocket_manager import manager
from server.dependencies import get_current_user_ws, get_connection


router = APIRouter(
    tags=["websockets"]
)


@router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    conn: Connection = Depends(get_connection),
    current_user = Depends(get_current_user_ws)
):
    if current_user is None:
        return  # already closed in the dependency

    user_id_as_string = str(current_user.id)
    await manager.connect(user_id_as_string, websocket)

    try:
        while True:
            # Wait for incoming messages from this client
            data = await websocket.receive_json()

            message_type = data.get("type")

            if message_type == "direct_message":
                # Send to a specific user
                await manager.send_to_user(
                    user_id=data["to"],
                    message={
                        "type": "direct_message",
                        "from": user_id_as_string,
                        "content": data["content"]
                    }
                )

            elif message_type == "broadcast":
                # Send to everyone
                await manager.broadcast({
                    "type": "broadcast",
                    "from": user_id_as_string,
                    "content": data["content"]
                })

    except WebSocketDisconnect:
        manager.disconnect(current_user.id)

        # Notify others this user went offline
        await manager.broadcast({
            "type": "user_offline",
            "user_id": user_id_as_string
        })