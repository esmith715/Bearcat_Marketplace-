import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from uuid import uuid4

from server.main import app
from server.dependencies import get_current_user

def make_mock_message(**overrides):
    defaults = {
        "id": uuid4(),
        "listing_id": uuid4(),
        "from_user_id": uuid4(),
        "to_user_id": uuid4(),
        "content": "Hey, is this still available?",
        "is_read": False,
        "read_at": None,
    }
    defaults.update(overrides)
    mock = MagicMock()
    for k, v in defaults.items():
        setattr(mock, k, v)
    return mock

# ===========================
# GET /messages/{listing_id}/{other_user_id}
# ===========================
class TestGetConversation:

    
    async def test_get_conversation_success(self, client, mock_conn, make_mock_user):
        """Should return message history for a conversation"""
        mock_user = make_mock_user()
        app.dependency_overrides[get_current_user] = lambda: mock_user

        with patch("server.routers.messages.messages_service.get_message_history", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = [make_mock_message(from_user_id=mock_user.id)]

            response = await client.get(
                f"/messages/{uuid4()}/{uuid4()}"
            )

            assert response.status_code == 200

        app.dependency_overrides.clear()

    
    async def test_get_conversation_unauthenticated(self, client, mock_conn):
        """No auth should return 401"""
        response = await client.get(f"/messages/{uuid4()}/{uuid4()}")
        assert response.status_code == 401

# ===========================
# GET /messages/{listing_id}/{other_user_id}/unread-count
# ===========================
class TestGetUnreadCountForConversation:

    
    async def test_get_unread_count_success(self, client, mock_conn, make_mock_user):
        """Should return unread count for a conversation"""
        mock_user = make_mock_user()
        app.dependency_overrides[get_current_user] = lambda: mock_user

        with patch("server.routers.messages.messages_service.get_unread_count_for_conversation", new_callable=AsyncMock) as mock_count:
            mock_count.return_value = 3

            response = await client.get(f"/messages/{uuid4()}/{uuid4()}/unread-count")

            assert response.status_code == 200
            assert response.json()["unread_count"] == 3

        app.dependency_overrides.clear()

# ===========================
# GET /messages/unread-count-total
# ===========================
class TestGetUnreadCountTotal:

    
    async def test_get_unread_count_total_success(self, client, mock_conn, make_mock_user):
        """Should return total unread count across all conversations"""
        mock_user = make_mock_user()
        app.dependency_overrides[get_current_user] = lambda: mock_user

        with patch("server.routers.messages.messages_service.get_unread_count_total", new_callable=AsyncMock) as mock_count:
            mock_count.return_value = 7

            response = await client.get("/messages/unread-count-total")

            assert response.status_code == 200
            assert response.json()["unread_count"] == 7

        app.dependency_overrides.clear()

# ===========================
# PATCH /messages/{message_id}/read
# ===========================
class TestMarkAsRead:

    
    async def test_mark_as_read_success(self, client, mock_conn, make_mock_user):
        """Should mark a message as read"""
        mock_user = make_mock_user()
        app.dependency_overrides[get_current_user] = lambda: mock_user

        with patch("server.routers.messages.messages_service.mark_as_read", new_callable=AsyncMock) as mock_mark:
            mock_mark.return_value = True

            response = await client.patch(f"/messages/{uuid4()}/read")

            assert response.status_code == 200
            assert response.json() == {"message": "Message marked as read"}

        app.dependency_overrides.clear()

    
    async def test_mark_as_read_not_found(self, client, mock_conn, make_mock_user):
        """Message not found or already read should return 404"""
        mock_user = make_mock_user()
        app.dependency_overrides[get_current_user] = lambda: mock_user

        with patch("server.routers.messages.messages_service.mark_as_read", new_callable=AsyncMock) as mock_mark:
            mock_mark.return_value = False

            response = await client.patch(f"/messages/{uuid4()}/read")

            assert response.status_code == 404

        app.dependency_overrides.clear()

# ===========================
# PATCH /messages/{listing_id}/{other_user_id}/read-all
# ===========================
class TestMarkConversationAsRead:

    
    async def test_mark_conversation_as_read_success(self, client, mock_conn, make_mock_user):
        """Should mark all messages in a conversation as read"""
        mock_user = make_mock_user()
        app.dependency_overrides[get_current_user] = lambda: mock_user

        with patch("server.routers.messages.messages_service.mark_conversation_as_read", new_callable=AsyncMock) as mock_mark:
            mock_mark.return_value = 5

            response = await client.patch(f"/messages/{uuid4()}/{uuid4()}/read-all")

            assert response.status_code == 200
            assert response.json()["marked_as_read_count"] == 5

        app.dependency_overrides.clear()