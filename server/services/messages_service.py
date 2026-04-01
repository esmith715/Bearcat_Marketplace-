from asyncpg import Connection
from uuid import UUID
from datetime import datetime
from typing import List
from server.schemas.message import Message, MessageResponse


async def save_message(
    conn: Connection,
    from_user_id: UUID,
    to_user_id: UUID,
    content: str
) -> Message:
    """
    Save a message to the database
    """
    
    message = await conn.fetchrow(
        """
        INSERT INTO messages (from_user_id, to_user_id, content, created_at)
        VALUES ($1, $2, $3, now())
        RETURNING id, from_user_id, to_user_id, content, is_read, created_at, read_at
        """,
        from_user_id,
        to_user_id,
        content
    )
    
    return Message(**dict(message))


async def get_message_history(
    conn: Connection,
    user_id: UUID,
    other_user_id: UUID,
    limit: int = 50,
    skip: int = 0
) -> List[MessageResponse]:
    """
    Get message history between two users.
    Returns messages sorted by created_at descending (newest first).
    """
    
    messages = await conn.fetch(
        """
        SELECT id, from_user_id, to_user_id, content, is_read, created_at, read_at
        FROM messages
        WHERE (
          (from_user_id = $1 AND to_user_id = $2) OR
          (from_user_id = $2 AND to_user_id = $1)
        )
        ORDER BY created_at DESC
        LIMIT $3 OFFSET $4
        """,
        user_id,
        other_user_id,
        limit,
        skip
    )
    
    return [MessageResponse(**dict(msg)) for msg in messages]


async def get_unread_count(
    conn: Connection,
    user_id: UUID,
    from_user_id: UUID | None = None
) -> int:
    """
    Get count of unread messages for a user.
    If from_user_id is provided, get unread count from that specific user.
    """
    
    if from_user_id:
        count = await conn.fetchval(
            """
            SELECT COUNT(*)
            FROM messages
            WHERE to_user_id = $1 AND from_user_id = $2 AND is_read = false
            """,
            user_id,
            from_user_id
        )
    else:
        count = await conn.fetchval(
            """
            SELECT COUNT(*)
            FROM messages
            WHERE to_user_id = $1 AND is_read = false
            """,
            user_id
        )
    
    return count


async def mark_as_read(
    conn: Connection,
    message_id: UUID,
    user_id: UUID
) -> bool:
    """
    Mark a single message as read (only if user is the recipient).
    Returns True if successful, False if message not found or user not recipient.
    """
    
    result = await conn.execute(
        """
        UPDATE messages
        SET is_read = true, read_at = now()
        WHERE id = $1 AND to_user_id = $2 AND is_read = false
        """,
        message_id,
        user_id
    )
    
    return result == "UPDATE 1"


async def mark_conversation_as_read(
    conn: Connection,
    user_id: UUID,
    other_user_id: UUID
) -> int:
    """
    Mark all unread messages from a specific user as read.
    Returns the number of messages updated.
    """
    
    result = await conn.execute(
        """
        UPDATE messages
        SET is_read = true, read_at = now()
        WHERE to_user_id = $1 AND from_user_id = $2 AND is_read = false
        """,
        user_id,
        other_user_id
    )
    
    # Extract the count from the result string "UPDATE X"
    count = int(result.split()[-1])
    return count
