import resend
from server.config import settings

resend.api_key = settings.RESEND_API_KEY

async def send_verification_email(to_email: str, token: str) -> None:
    """Send an email verification link to the user."""

    verification_link = f"{settings.FRONTEND_URL}/verify-email?token={token}"

    resend.Emails.send({
        "from": settings.FROM_EMAIL,
        "to": to_email,
        "subject": "Verify your email",
        "html": f"""
            <h2>Welcome! Please verify your email</h2>
            <p>Click the link below to verify your email address:</p>
            <a href="{verification_link}">Verify Email</a>
            <p>This link expires in 24 hours.</p>
        """
    })

async def send_password_reset_email(to_email: str, token: str) -> None:
    """Send a password reset link to the user."""

    reset_link = f"{settings.FRONTEND_URL}/reset-password?token={token}"

    resend.Emails.send({
        "from": settings.FROM_EMAIL,
        "to": to_email,
        "subject": "Reset your password",
        "html": f"""
            <h2>Password Reset Request</h2>
            <p>Click the link below to reset your password:</p>
            <a href="{reset_link}">Reset Password</a>
            <p>This link expires in 1 hour.</p>
            <p>If you didn't request this, you can safely ignore this email.</p>
        """
    })