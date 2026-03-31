import pytest
import aiohttp

from server.services import emailing_service

MAILHOG_API = "http://localhost:8025/api/v2"

#=====================#
# Helpers             #
#=====================#

async def get_mailhog_messages():
    """Fetch all caught emails from Mailhog's API."""
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{MAILHOG_API}/messages") as resp:
            data = await resp.json()
            return data.get("items", [])

async def clear_mailhog():
    """Wipe all caught emails before each test."""
    async with aiohttp.ClientSession() as session:
        await session.delete(f"{MAILHOG_API}/messages")

#=====================#
# Fixtures            #
#=====================#

@pytest.fixture(autouse=True)
async def clean_inbox():
    """Automatically clear Mailhog inbox before every test."""
    await clear_mailhog()
    yield
    await clear_mailhog()

#===============================#
# send_verification_email Tests #
#===============================#

class TestSendVerificationEmailIntegration:

    async def test_email_is_delivered_to_mailhog(self):
        result = await emailing_service.send_verification_email(
            "student@mail.uc.edu",
            "verify-token-abc"
        )

        assert result is True

        messages = await get_mailhog_messages()
        assert len(messages) == 1

    async def test_email_sent_to_correct_recipient(self):
        await emailing_service.send_verification_email(
            "student@mail.uc.edu",
            "verify-token-abc"
        )

        messages = await get_mailhog_messages()
        recipients = messages[0]["To"]
        addresses = [r["Mailbox"] + "@" + r["Domain"] for r in recipients]

        assert "student@mail.uc.edu" in addresses

    async def test_email_subject_is_correct(self):
        await emailing_service.send_verification_email(
            "student@mail.uc.edu",
            "verify-token-abc"
        )

        messages = await get_mailhog_messages()
        subject = messages[0]["Content"]["Headers"]["Subject"][0]

        assert "Verify Your Email" in subject

    async def test_email_body_contains_token(self):
        await emailing_service.send_verification_email(
            "student@mail.uc.edu",
            "unique-token-xyz"
        )

        messages = await get_mailhog_messages()
        body = messages[0]["Content"]["Body"]

        assert "unique-token-xyz" in body

    async def test_returns_false_when_smtp_unreachable(self):
        """Temporarily point at a dead port to simulate SMTP failure."""
        with pytest.MonkeyPatch().context() as mp:
            mp.setattr("server.config.settings.SMTP_PORT", 9999)

            result = await emailing_service.send_verification_email(
                "student@mail.uc.edu",
                "token"
            )

        assert result is False

#============================#
# send_password_reset Tests  #
#============================#

class TestSendPasswordResetEmailIntegration:

    async def test_email_is_delivered_to_mailhog(self):
        result = await emailing_service.send_password_reset_email(
            "student@mail.uc.edu",
            "reset-token-abc"
        )

        assert result is True

        messages = await get_mailhog_messages()
        assert len(messages) == 1

    async def test_email_subject_is_correct(self):
        await emailing_service.send_password_reset_email(
            "student@mail.uc.edu",
            "reset-token-abc"
        )

        messages = await get_mailhog_messages()
        subject = messages[0]["Content"]["Headers"]["Subject"][0]

        assert "Reset Your Password" in subject

    async def test_email_body_contains_reset_token(self):
        await emailing_service.send_password_reset_email(
            "student@mail.uc.edu",
            "my-unique-reset-token"
        )

        messages = await get_mailhog_messages()
        body = messages[0]["Content"]["Body"]

        assert "my-unique-reset-token" in body