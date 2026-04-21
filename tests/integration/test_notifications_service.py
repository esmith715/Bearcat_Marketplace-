import pytest
from uuid import uuid4

from server.services import notifications_service
from server.schemas.notification import NotificationCreate, NotificationType


class TestCreateNotification:

    async def test_create_notification_new_message(self, test_conn, registered_user, sample_listing):
        """Should create a new_message notification"""
        message_id = uuid4()

        notification = await notifications_service.create_notification(
            test_conn,
            NotificationCreate(
                user_id=registered_user.id,
                type=NotificationType.new_message,
                message_id=message_id
            )
        )

        assert notification.user_id == registered_user.id
        assert notification.type == NotificationType.new_message
        assert notification.is_read is False

    async def test_create_notification_listing_updated(self, test_conn, registered_user, sample_listing):
        """Should create a listing_updated notification"""
        notification = await notifications_service.create_notification(
            test_conn,
            NotificationCreate(
                user_id=registered_user.id,
                type=NotificationType.listing_updated,
                listing_id=sample_listing.id
            )
        )

        assert notification.listing_id == sample_listing.id
        assert notification.type == NotificationType.listing_updated


class TestGetNotifications:

    async def test_get_notifications_returns_list(self, test_conn, registered_user, sample_listing):
        """Should return a list of notifications for the user"""
        await notifications_service.create_notification(
            test_conn,
            NotificationCreate(
                user_id=registered_user.id,
                type=NotificationType.listing_updated,
                listing_id=sample_listing.id
            )
        )

        notifications = await notifications_service.get_notifications(test_conn, registered_user.id)
        assert len(notifications) >= 1

    async def test_get_notifications_unread_only(self, test_conn, registered_user, sample_listing):
        """unread_only=True should only return unread notifications"""
        notification = await notifications_service.create_notification(
            test_conn,
            NotificationCreate(
                user_id=registered_user.id,
                type=NotificationType.listing_updated,
                listing_id=sample_listing.id
            )
        )

        # Mark it as read
        await notifications_service.mark_as_read(test_conn, notification.id, registered_user.id)

        unread = await notifications_service.get_notifications(
            test_conn, registered_user.id, unread_only=True
        )

        assert all(n.is_read is False for n in unread)

    async def test_get_notifications_empty_for_new_user(self, test_conn, registered_user):
        """Brand new user should have no notifications"""
        notifications = await notifications_service.get_notifications(test_conn, registered_user.id)
        assert notifications == []


class TestGetUnreadCount:

    async def test_get_unread_count(self, test_conn, registered_user, sample_listing):
        """Should return correct unread count"""
        await notifications_service.create_notification(
            test_conn,
            NotificationCreate(
                user_id=registered_user.id,
                type=NotificationType.listing_updated,
                listing_id=sample_listing.id
            )
        )

        count = await notifications_service.get_unread_count(test_conn, registered_user.id)
        assert count >= 1

    async def test_get_unread_count_zero_when_all_read(self, test_conn, registered_user, sample_listing):
        """Should return 0 after all notifications are marked read"""
        notification = await notifications_service.create_notification(
            test_conn,
            NotificationCreate(
                user_id=registered_user.id,
                type=NotificationType.listing_updated,
                listing_id=sample_listing.id
            )
        )

        await notifications_service.mark_all_as_read(test_conn, registered_user.id)

        count = await notifications_service.get_unread_count(test_conn, registered_user.id)
        assert count == 0


class TestMarkAsRead:

    async def test_mark_as_read_success(self, test_conn, registered_user, sample_listing):
        """Should mark a single notification as read"""
        notification = await notifications_service.create_notification(
            test_conn,
            NotificationCreate(
                user_id=registered_user.id,
                type=NotificationType.listing_updated,
                listing_id=sample_listing.id
            )
        )

        await notifications_service.mark_as_read(test_conn, notification.id, registered_user.id)

        remaining = await notifications_service.get_notifications(
            test_conn, registered_user.id, unread_only=True
        )
        assert all(n.id != notification.id for n in remaining)


class TestMarkAllAsRead:

    async def test_mark_all_as_read(self, test_conn, registered_user, sample_listing):
        """Should mark all notifications as read"""
        for _ in range(3):
            await notifications_service.create_notification(
                test_conn,
                NotificationCreate(
                    user_id=registered_user.id,
                    type=NotificationType.listing_updated,
                    listing_id=sample_listing.id
                )
            )

        await notifications_service.mark_all_as_read(test_conn, registered_user.id)

        count = await notifications_service.get_unread_count(test_conn, registered_user.id)
        assert count == 0