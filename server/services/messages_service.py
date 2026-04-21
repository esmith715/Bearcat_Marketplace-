from asyncpg import Connection
from uuid import UUID
from typing import List
from server.schemas.message import Message


async def save_message(
    conn: Connection,
    listing_id: UUID,
    from_user_id: UUID,
    to_user_id: UUID,
    content: str
) -> Message:
    """
    Save a message to the database
    """
    
    message_record = await conn.fetchrow(
        """
        INSERT INTO messages (listing_id, from_user_id, to_user_id, content)
        VALUES ($1, $2, $3, $4)
        RETURNING *
        """,
        listing_id,
        from_user_id,
        to_user_id,
        content
    )
    
    return Message.model_validate(dict(message_record))


async def get_message_history(
    conn: Connection,
    listing_id: UUID,
    user1_id: UUID,
    user2_id: UUID,
    limit: int = 50,
    skip: int = 0
) -> List[Message]:
    """
    Get message history for a specific conversation.
    Returns messages sorted by created_at descending (newest first).
    """
    
    message_records = await conn.fetch(
        """
        SELECT *
        FROM messages
        WHERE listing_id = $1 
            AND (
            (from_user_id = $2 AND to_user_id = $3)
            OR
            (from_user_id = $3 AND to_user_id = $2)
            )
        ORDER BY created_at DESC
        LIMIT $4 
        OFFSET $5
        """,
        listing_id,
        user1_id,
        user2_id,
        limit,
        skip
    )
    
    return [Message.model_validate(dict(record)) for record in message_records]


async def get_all_conversations(
    conn: Connection,
    user_id: UUID,
) -> list[dict]:
    """
    Get a summary of all unique conversations for a user.
    Each row represents one conversation thread, identified by the
    combination of (listing_id, other_user_id).
    Returns the latest message in each thread plus an unread count.
    This is like an "inbox" view.
    """
    records = await conn.fetch(
        """
        SELECT DISTINCT ON (listing_id, other_user_id)
            -- DISTINCT ON is a PostgreSQL feature: for each unique
            -- (listing_id, other_user_id) pair, keep only the first row
            -- (which, given ORDER BY created_at DESC, is the newest message).
            m.id,
            m.listing_id,
            m.content,
            m.created_at,
            m.is_read,
            m.from_user_id,
            m.to_user_id,
            l.title AS listing_title,
            -- CASE is SQL's if/else — figure out who the "other" user is
            CASE
                WHEN m.from_user_id = $1 THEN m.to_user_id
                ELSE m.from_user_id
            END AS other_user_id,
            CASE
                WHEN m.from_user_id = $1 THEN u_to.username
                ELSE u_from.username
            END AS other_username,
            -- Subquery: count unread messages in this thread sent TO us
            (
                SELECT COUNT(*)
                FROM messages unread
                WHERE unread.listing_id = m.listing_id
                  AND unread.from_user_id = CASE
                        WHEN m.from_user_id = $1 THEN m.to_user_id
                        ELSE m.from_user_id
                      END
                  AND unread.to_user_id = $1
                  AND unread.is_read = FALSE
            ) AS unread_count
        FROM messages m
        JOIN listings l ON l.id = m.listing_id
        JOIN users u_from ON u_from.id = m.from_user_id
        JOIN users u_to   ON u_to.id   = m.to_user_id
        WHERE m.from_user_id = $1 OR m.to_user_id = $1
        ORDER BY listing_id, other_user_id, m.created_at DESC
        """,
        user_id,
    )

    # Convert each asyncpg Record to a plain dict so we can serialize it.
    # asyncpg records are like named tuples — dict() unpacks them.
    return [dict(r) for r in records]


async def get_unread_count_for_conversation(
    conn: Connection,
    listing_id: UUID,
    current_user_id: UUID,
    other_user_id: UUID,
) -> int:
    """
    Get number of unread messages corresponding to a specific converstation
    """

    count = await conn.fetchval(
        """
        SELECT COUNT(*)
        FROM messages
        WHERE listing_id = $1
            AND from_user_id = $2
            AND to_user_id = $3
            AND is_read = FALSE
        """,
        listing_id,
        other_user_id, # The one who sent the messages
        current_user_id # The reciever who hasnt read the messages
    )

    return count


async def get_unread_count_total(
    conn: Connection,
    user_id: UUID
) -> int:
    """
    Get the total number of unread messages across all conversations for a user
    """
    
    count = await conn.fetchval(
        """
        SELECT COUNT(*)
        FROM messages
        WHERE to_user_id = $1
            AND is_read = FALSE
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
        SET is_read = true, read_at = NOW()
        WHERE id = $1 
            AND to_user_id = $2 
            AND is_read = FALSE
        """,
        message_id,
        user_id
    )
    
    return result == "UPDATE 1"


async def mark_conversation_as_read(
    conn: Connection,
    listing_id: UUID,
    current_user_id: UUID,
    other_user_id: UUID
) -> int:
    """
    Mark all unread messages from a specific user as read.
    Returns the number of messages updated.
    """
    
    result = await conn.execute(
        """
        UPDATE messages
        SET is_read = TRUE, read_at = NOW()
        WHERE listing_id = $1
            AND from_user_id = $2
            AND to_user_id = $3
            AND is_read = FALSE
        """,
        listing_id,
        other_user_id, # The one who sent the messages
        current_user_id # The reciever who hasnt read the messages
    )
    
    # Extract the count from the result string "UPDATE X"
    count = int(result.split()[-1])
    return count
