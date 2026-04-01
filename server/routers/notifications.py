from fastapi import APIRouter, Depends
import asyncpg
from typing import List

from server.dependencies import get_current_user, get_connection
from server.schemas.notification import Notification
from server.services import notifications_service


router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.get("/", response_model=List[Notification])
async def get_notifications(
    unread_only: bool = False,
    limit: int = 20,
    current_user=Depends(get_current_user),
    conn: asyncpg.Connection = Depends(get_connection)
):
    """
    Get notifications for the logged in user
    """

    notifications = await notifications_service.get_notifications(
        conn, current_user.id, limit, unread_only
    )
    return notifications


@router.get("/unread-count")
async def get_unread_count(
    current_user=Depends(get_current_user),
    conn: asyncpg.Connection = Depends(get_connection)
):
    """
    Get the number of unread notifications
    """

    count = await notifications_service.get_unread_count(conn, current_user.id)
    return {"unread_count": count}


@router.patch("/{notification_id}/read")
async def mark_as_read(
    notification_id: str,
    current_user=Depends(get_current_user),
    conn: asyncpg.Connection = Depends(get_connection)
):
    """
    Mark a single notification as read
    """

    await notifications_service.mark_as_read(conn, notification_id, current_user.id)
    return {"message": "Notification marked as read"}


@router.patch("/read-all")
async def mark_all_as_read(
    current_user=Depends(get_current_user),
    conn: asyncpg.Connection = Depends(get_connection)
):
    """
    Mark all notifications as read
    """

    await notifications_service.mark_all_as_read(conn, current_user.id)
    return {"message": "All notifications marked as read"}