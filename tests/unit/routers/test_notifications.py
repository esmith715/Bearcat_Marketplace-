import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from uuid import uuid4

from server.main import app
from server.dependencies import get_current_user

def make_mock_notification(**overrides):
    defaults = {
        "id": uuid4(),
        "user_id": uuid4(),
        "type": "new_message",
        "is_read": False,
        "message_id": None,
        "listing_id": None,
    }
    defaults.update(overrides)
    mock = MagicMock()
    for k, v in defaults.items():
        setattr(mock, k, v)
    return mock

# ===========================
# GET /notifications/
# ===========================
class TestGetNotifications:

    
    async def test_get_notifications_success(self, client, mock_conn, make_mock_user):
        """Should return notifications for the logged in user"""
        mock_user = make_mock_user()
        app.dependency_overrides[get_current_user] = lambda: mock_user

        with patch("server.routers.notifications.notifications_service.get_notifications", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = [make_mock_notification(user_id=mock_user.id)]

            response = await client.get("/notifications/")

            assert response.status_code == 200

        app.dependency_overrides.clear()

    
    async def test_get_notifications_unauthenticated(self, client, mock_conn):
        """No auth should return 401"""
        response = await client.get("/notifications/")
        assert response.status_code == 401

    
    async def test_get_notifications_unread_only(self, client, mock_conn, make_mock_user):
        """unread_only=true should pass the flag to the service"""
        mock_user = make_mock_user()
        app.dependency_overrides[get_current_user] = lambda: mock_user

        with patch("server.routers.notifications.notifications_service.get_notifications", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = []

            response = await client.get("/notifications/", params={"unread_only": True})

            assert response.status_code == 200
            mock_get.assert_called_once_with(
                mock_conn, mock_user.id, 20, True
            )

        app.dependency_overrides.clear()

# ===========================
# GET /notifications/unread-count
# ===========================
class TestGetUnreadCount:

    
    async def test_get_unread_count_success(self, client, mock_conn, make_mock_user):
        """Should return unread notification count"""
        mock_user = make_mock_user()
        app.dependency_overrides[get_current_user] = lambda: mock_user

        with patch("server.routers.notifications.notifications_service.get_unread_count", new_callable=AsyncMock) as mock_count:
            mock_count.return_value = 4

            response = await client.get("/notifications/unread-count")

            assert response.status_code == 200
            assert response.json()["unread_count"] == 4

        app.dependency_overrides.clear()

# ===========================
# PATCH /notifications/{notification_id}/read
# ===========================
class TestMarkNotificationAsRead:

    
    async def test_mark_as_read_success(self, client, mock_conn, make_mock_user):
        """Should mark a notification as read"""
        mock_user = make_mock_user()
        app.dependency_overrides[get_current_user] = lambda: mock_user

        with patch("server.routers.notifications.notifications_service.mark_as_read", new_callable=AsyncMock) as mock_mark:
            mock_mark.return_value = None

            response = await client.patch(f"/notifications/{uuid4()}/read")

            assert response.status_code == 200
            assert response.json() == {"message": "Notification marked as read"}

        app.dependency_overrides.clear()

# ===========================
# PATCH /notifications/read-all
# ===========================
class TestMarkAllNotificationsAsRead:

    
    async def test_mark_all_as_read_success(self, client, mock_conn, make_mock_user):
        """Should mark all notifications as read"""
        mock_user = make_mock_user()
        app.dependency_overrides[get_current_user] = lambda: mock_user

        with patch("server.routers.notifications.notifications_service.mark_all_as_read", new_callable=AsyncMock) as mock_mark:
            mock_mark.return_value = None

            response = await client.patch("/notifications/read-all")

            assert response.status_code == 200
            assert response.json() == {"message": "All notifications marked as read"}

        app.dependency_overrides.clear()