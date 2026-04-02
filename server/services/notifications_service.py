from asyncpg import Connection
from uuid import UUID

from server.dependencies import get_current_user
from server.schemas.user import UserInDB
from server.services.websocket_manager import manager
from server.schemas.notification import NotificationCreate, NotificationType, Notification

async def create_notification(
    conn: Connection,
    notification_data: NotificationCreate
) -> dict:
    """
    Create a notification in the DB and deliver it in real-time if user is online
    """

    # Save to database
    notification_record = await conn.fetchrow(
        """
        INSERT INTO notifications (user_id, type, message_id, listing_id)
        VALUES ($1, $2, $3, $4)
        RETURNING *
        """,
        notification_data.user_id,
        notification_data.type.value,
        notification_data.message_id,
        notification_data.listing_id 
    )

    notification = Notification.model_validate(dict(notification_record))

    # Deliver in real-time if user is online
    if manager.is_online(notification.user_id):
        await manager.send_to_user(notification.user_id, notification.to_websocket_payload())

    return notification


async def get_notifications(
    conn: Connection,
    user_id: UUID,
    limit: int = 20,
    unread_only: bool = False
) -> list[Notification]:
    """
    Fetch notifications for a user
    """

    query = """
        SELECT *
        FROM notifications
        WHERE user_id = $1
    """

    if unread_only:
        query += " AND is_read = FALSE"

    query += " ORDER BY created_at DESC LIMIT $2"

    notification_records = await conn.fetch(query, user_id, limit)
    return [Notification.model_validate(dict(record)) for record in notification_records]


async def get_unread_count(
    conn: Connection,
    user_id: UUID
) -> int:
    """
    Get the number of unread notifications for a user
    """

    row = await conn.fetchrow(
        """
        SELECT COUNT(*)
        FROM notifications
        WHERE user_id = $1 AND is_read = FALSE
        """,
        user_id
    )

    return row["count"]


async def mark_as_read(
    conn: Connection,
    notification_id: UUID,
    user_id: UUID
) -> None:
    """
    Marks notification as read
    """

    await conn.execute(
        """
        UPDATE notifications
        SET is_read = TRUE
        WHERE id = $1 AND user_id = $2
        """,
        notification_id, 
        user_id
    )


async def mark_all_as_read(
    conn: Connection,
    user_id: UUID
) -> None:
    """
    Marks all of a users notifications as read
    """

    await conn.execute(
        """
        UPDATE notifications
        SET is_read = TRUE
        WHERE user_id = $1 AND is_read = FALSE
        """,
        user_id
    )