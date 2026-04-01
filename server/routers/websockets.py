from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from asyncpg import Connection
from uuid import UUID

from server.services.websocket_manager import manager
from server.dependencies import get_current_user_ws, get_connection
from server.services import messages_service


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
                # Save message to database
                try:
                    to_user_id = UUID(data["to"])
                    saved_message = await messages_service.save_message(
                        conn,
                        current_user.id,
                        to_user_id,
                        data["content"]
                    )
                    
                    # Send to a specific user with message_id
                    await manager.send_to_user(
                        user_id=data["to"],
                        message={
                            "type": "direct_message",
                            "id": str(saved_message.id),
                            "from": user_id_as_string,
                            "content": data["content"],
                            "created_at": saved_message.created_at.isoformat()
                        }
                    )
                except (ValueError, KeyError) as e:
                    print(f"Error saving message: {e}")

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