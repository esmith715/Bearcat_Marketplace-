from asyncpg import Connection
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from uuid import UUID

from server.db.database import get_connection
from server.dependencies import get_current_user
from server.schemas.message import MessageResponse
from server.services import messages_service


router = APIRouter(
    prefix="/messages",
    tags=["messages"],
)


@router.get("/{user_id}", response_model=List[MessageResponse])
async def get_conversation(
    user_id: str,
    limit: int = 50,
    skip: int = 0,
    conn: Connection = Depends(get_connection),
    current_user = Depends(get_current_user),
):
    """
    Get message history with a specific user.
    Returns messages sorted by created_at (newest first).
    """
    
    try:
        user_uuid = UUID(user_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user ID format"
        )
    
    messages = await messages_service.get_message_history(
        conn,
        current_user.id,
        user_uuid,
        limit,
        skip
    )
    
    return messages


@router.get("/{user_id}/unread-count")
async def get_unread_count(
    user_id: str,
    conn: Connection = Depends(get_connection),
    current_user = Depends(get_current_user),
):
    """
    Get count of unread messages from a specific user.
    """
    
    try:
        user_uuid = UUID(user_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user ID format"
        )
    
    count = await messages_service.get_unread_count(
        conn,
        current_user.id,
        user_uuid
    )
    
    return {"unread_count": count}


@router.patch("/{message_id}/read")
async def mark_as_read(
    message_id: str,
    conn: Connection = Depends(get_connection),
    current_user = Depends(get_current_user),
):
    """
    Mark a single message as read.
    """
    
    try:
        message_uuid = UUID(message_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid message ID format"
        )
    
    success = await messages_service.mark_as_read(conn, message_uuid, current_user.id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Message not found or already read"
        )
    
    return {"message": "Message marked as read"}


@router.patch("/{user_id}/read-all")
async def mark_conversation_as_read(
    user_id: str,
    conn: Connection = Depends(get_connection),
    current_user = Depends(get_current_user),
):
    """
    Mark all unread messages from a specific user as read.
    """
    
    try:
        user_uuid = UUID(user_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user ID format"
        )
    
    count = await messages_service.mark_conversation_as_read(
        conn,
        current_user.id,
        user_uuid
    )
    
    return {"marked_as_read": count}
