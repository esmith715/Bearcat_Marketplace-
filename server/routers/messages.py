from asyncpg import Connection
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from uuid import UUID

from server.db.database import get_connection
from server.dependencies import get_current_user
from server.schemas.message import Message
from server.schemas.user import UserInDB
from server.services import messages_service


router = APIRouter(
    prefix="/messages",
    tags=["messages"],
)


@router.get("/{listing_id}/{other_user_id}", response_model=List[Message])
async def get_conversation(
    listing_id: UUID,
    other_user_id: UUID,
    limit: int = 50,
    skip: int = 0,
    conn: Connection = Depends(get_connection),
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Get message history with a specific user.
    Returns messages sorted by newest first.
    """
    
    try:
        messages = await messages_service.get_message_history(
            conn,
            listing_id,
            current_user.id,
            other_user_id,
            limit,
            skip
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail=str(e)
        )
    
    except Exception as e:
        print(f"Error retrieving conversation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retreive conversation"
        )

    return messages


from server.schemas.message import Message  # already imported


@router.get("/conversations")
async def get_all_conversations(
    conn: Connection = Depends(get_connection),
    current_user: UserInDB = Depends(get_current_user),
):
    """
    Get all conversation threads for the logged-in user.
    Returns one entry per unique (listing, other_user) pair,
    with the latest message preview and unread count.
    """
    try:
        conversations = await messages_service.get_all_conversations(
            conn,
            current_user.id,
        )
    except Exception as e:
        print(f"Error fetching conversations: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch conversations",
        )

    # FastAPI can't auto-serialize UUID objects or datetime objects from raw dicts,
    # so we convert them to strings manually here.
    return [
        {
            **conv,
            "listing_id":    str(conv["listing_id"]),
            "other_user_id": str(conv["other_user_id"]),
            "from_user_id":  str(conv["from_user_id"]),
            "to_user_id":    str(conv["to_user_id"]),
            "id":            str(conv["id"]),
            "created_at":    conv["created_at"].isoformat() if conv["created_at"] else None,
            "unread_count":  int(conv["unread_count"]),
        }
        for conv in conversations
    ]


@router.get("/{listing_id}/{other_user_id}/unread-count")
async def get_unread_count_for_conversation(
    listing_id: UUID,
    other_user_id: UUID,
    conn: Connection = Depends(get_connection),
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Get logged in user's count of unread messages from a specific conversation
    """
    
    count = await messages_service.get_unread_count_for_conversation(
        conn,
        listing_id,
        current_user.id,
        other_user_id
    )

    return {"unread_count": count}


@router.get("/unread-count-total")
async def get_unread_count_total(
    conn: Connection = Depends(get_connection),
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Get logged in user's total number of unread messages
    """
    
    count = await messages_service.get_unread_count_total(
        conn,
        current_user.id
    )

    return {"unread_count": count}


@router.patch("/{message_id}/read")
async def mark_as_read(
    message_id: UUID,
    conn: Connection = Depends(get_connection),
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Mark a single message as read
    """
    
    success = await messages_service.mark_as_read(conn, message_id, current_user.id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Message not found or already read"
        )
    
    return {"message": "Message marked as read"}


@router.patch("/{listing_id}/{other_user_id}/read-all")
async def mark_conversation_as_read(
    listing_id: UUID,
    other_user_id: UUID,
    conn: Connection = Depends(get_connection),
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Mark all unread messages from a specific conversation as read
    """
    
    count = await messages_service.mark_conversation_as_read(
        conn,
        listing_id,
        current_user.id,
        other_user_id
    )
    
    return {"marked_as_read_count": count}
