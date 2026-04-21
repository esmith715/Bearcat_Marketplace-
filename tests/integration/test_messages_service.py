import pytest
from uuid import uuid4

from server.services import messages_service


class TestSaveMessage:

    async def test_save_message_success(self, test_conn, registered_user, sample_listing):
        """
        Should persist a message and return it
        """

        other_user = await test_conn.fetchrow(
            "INSERT INTO users (email, username, password_hash) VALUES ($1, $2, $3) RETURNING *",
            "other@mail.uc.edu", "otheruser", "hashed"
        )

        message = await messages_service.save_message(
            test_conn,
            sample_listing.id,
            registered_user.id,
            other_user["id"],
            "Hey, is this still available?"
        )

        assert message.content == "Hey, is this still available?"
        assert message.from_user_id == registered_user.id
        assert message.is_read is False

    async def test_save_message_is_unread_by_default(self, test_conn, registered_user, sample_listing):
        """
        New messages should default to unread
        """

        other_user = await test_conn.fetchrow(
            "INSERT INTO users (email, username, password_hash) VALUES ($1, $2, $3) RETURNING *",
            "other2@mail.uc.edu", "otheruser2", "hashed"
        )

        message = await messages_service.save_message(
            test_conn,
            sample_listing.id,
            registered_user.id,
            other_user["id"],
            "Hello!"
        )

        assert message.is_read is False
        assert message.read_at is None



class TestGetMessageHistory:

    async def test_get_message_history_returns_both_directions(self, test_conn, registered_user, sample_listing):
        """
        Should return messages sent in both directions
        """

        other_user = await test_conn.fetchrow(
            "INSERT INTO users (email, username, password_hash) VALUES ($1, $2, $3) RETURNING *",
            "other3@mail.uc.edu", "otheruser3", "hashed"
        )

        await messages_service.save_message(test_conn, sample_listing.id, registered_user.id, other_user["id"], "Hi!")
        await messages_service.save_message(test_conn, sample_listing.id, other_user["id"], registered_user.id, "Hey back!")

        history = await messages_service.get_message_history(
            test_conn, sample_listing.id, registered_user.id, other_user["id"]
        )

        assert len(history) == 2

    async def test_get_message_history_empty(self, test_conn, registered_user, sample_listing):
        """No messages should return empty list"""
        history = await messages_service.get_message_history(
            test_conn, sample_listing.id, registered_user.id, uuid4()
        )
        assert history == []

    async def test_get_message_history_pagination(self, test_conn, registered_user, sample_listing):
        """Pagination should limit results correctly"""
        other_user = await test_conn.fetchrow(
            "INSERT INTO users (email, username, password_hash) VALUES ($1, $2, $3) RETURNING *",
            "other4@mail.uc.edu", "otheruser4", "hashed"
        )

        for i in range(5):
            await messages_service.save_message(
                test_conn, sample_listing.id, registered_user.id, other_user["id"], f"Message {i}"
            )

        page = await messages_service.get_message_history(
            test_conn, sample_listing.id, registered_user.id, other_user["id"], limit=2, skip=0
        )

        assert len(page) == 2


class TestMarkAsRead:

    async def test_mark_as_read_success(self, test_conn, registered_user, sample_listing):
        """Should mark a message as read and return True"""
        other_user = await test_conn.fetchrow(
            "INSERT INTO users (email, username, password_hash) VALUES ($1, $2, $3) RETURNING *",
            "other5@mail.uc.edu", "otheruser5", "hashed"
        )

        message = await messages_service.save_message(
            test_conn, sample_listing.id, other_user["id"], registered_user.id, "Read me!"
        )

        result = await messages_service.mark_as_read(test_conn, message.id, registered_user.id)
        assert result is True

    async def test_mark_as_read_wrong_user_returns_false(self, test_conn, registered_user, sample_listing):
        """Non-recipient should not be able to mark as read"""
        other_user = await test_conn.fetchrow(
            "INSERT INTO users (email, username, password_hash) VALUES ($1, $2, $3) RETURNING *",
            "other6@mail.uc.edu", "otheruser6", "hashed"
        )

        message = await messages_service.save_message(
            test_conn, sample_listing.id, registered_user.id, other_user["id"], "Not for you to mark!"
        )

        # registered_user is the sender, not recipient — should fail
        result = await messages_service.mark_as_read(test_conn, message.id, registered_user.id)
        assert result is False

    async def test_mark_as_read_nonexistent_message(self, test_conn, registered_user):
        """Non-existent message ID should return False"""
        result = await messages_service.mark_as_read(test_conn, uuid4(), registered_user.id)
        assert result is False


class TestMarkConversationAsRead:

    async def test_mark_conversation_as_read_returns_count(self, test_conn, registered_user, sample_listing):
        """Should return the number of messages marked as read"""
        other_user = await test_conn.fetchrow(
            "INSERT INTO users (email, username, password_hash) VALUES ($1, $2, $3) RETURNING *",
            "other7@mail.uc.edu", "otheruser7", "hashed"
        )

        for _ in range(3):
            await messages_service.save_message(
                test_conn, sample_listing.id, other_user["id"], registered_user.id, "Unread!"
            )

        count = await messages_service.mark_conversation_as_read(
            test_conn, sample_listing.id, registered_user.id, other_user["id"]
        )

        assert count == 3

    async def test_mark_conversation_as_read_no_messages(self, test_conn, registered_user, sample_listing):
        """No unread messages should return 0"""
        count = await messages_service.mark_conversation_as_read(
            test_conn, sample_listing.id, registered_user.id, uuid4()
        )
        assert count == 0


class TestGetUnreadCounts:

    async def test_get_unread_count_for_conversation(self, test_conn, registered_user, sample_listing):
        """
        Should count only unread messages in a specific conversation
        """

        other_user = await test_conn.fetchrow(
            "INSERT INTO users (email, username, password_hash) VALUES ($1, $2, $3) RETURNING *",
            "other8@mail.uc.edu", "otheruser8", "hashed"
        )

        await messages_service.save_message(
            test_conn, sample_listing.id, other_user["id"], registered_user.id, "Unread 1"
        )
        await messages_service.save_message(
            test_conn, sample_listing.id, other_user["id"], registered_user.id, "Unread 2"
        )

        count = await messages_service.get_unread_count_for_conversation(
            test_conn, sample_listing.id, registered_user.id, other_user["id"]
        )

        assert count == 2

    async def test_get_unread_count_total(self, test_conn, registered_user, sample_listing):
        """Should count all unread messages across all conversations"""
        other_user = await test_conn.fetchrow(
            "INSERT INTO users (email, username, password_hash) VALUES ($1, $2, $3) RETURNING *",
            "other9@mail.uc.edu", "otheruser9", "hashed"
        )

        await messages_service.save_message(
            test_conn, sample_listing.id, other_user["id"], registered_user.id, "Unread total"
        )

        count = await messages_service.get_unread_count_total(test_conn, registered_user.id)
        assert count >= 1