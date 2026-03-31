import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from server.config import settings
import asyncio
from typing import Optional

async def send_verification_email(
    email: str, 
    verification_token: str
) -> bool:
    """
    Sends email verification link to user. Returns success of the operation.
    """

    try:
        verification_link = f"{settings.FRONTEND_URL}/verify-email?token={verification_token}"
        
        # Email content
        # TODO: Maybe this should be passed in from the frontend?
        subject = "Verify Your Email - Bearcat Marketplace"
        html_content = f"""
        <html>
            <body style="font-family: Arial, sans-serif;">
                <h2>Welcome to Bearcat Marketplace!</h2>
                <p>Please verify your email address by clicking the link below:</p>
                <p>
                    <a href="{verification_link}" 
                        style="background-color: #007bff; color: white; padding: 10px 20px; 
                                text-decoration: none; border-radius: 5px; display: inline-block;">
                        Verify Email
                    </a>
                </p>
                <p>Or copy and paste this link:</p>
                <p>{verification_link}</p>
                <p style="color: #888; font-size: 12px;">
                    This link expires in 24 hours.
                </p>
            </body>
        </html>
        """
        
        await _send_email(email, subject, html_content)
        return True
        
    except Exception as e:
        print(f"Error sending verification email: {e}")
        return False

async def send_password_reset_email(email: str, reset_token: str) -> bool:
    """
    Send password reset link to user. Returns success of the operation.
    """

    try:
        reset_link = f"{settings.FRONTEND_URL}/reset-password?token={reset_token}"
        
        # Email content
        # TODO: Maybe this should be passed in from the frontend?
        subject = "Reset Your Password - Bearcat Marketplace"
        html_content = f"""
        <html>
            <body style="font-family: Arial, sans-serif;">
                <h2>Password Reset Request</h2>
                <p>We received a request to reset your password. Click the link below:</p>
                <p>
                    <a href="{reset_link}" 
                        style="background-color: #28a745; color: white; padding: 10px 20px; 
                                text-decoration: none; border-radius: 5px; display: inline-block;">
                        Reset Password
                    </a>
                </p>
                <p>Or copy and paste this link:</p>
                <p>{reset_link}</p>
                <p style="color: #888; font-size: 12px;">
                    This link expires in 24 hours. If you didn't request this, ignore this email.
                </p>
            </body>
        </html>
        """
        
        await _send_email(email, subject, html_content)
        return True
        
    except Exception as e:
        print(f"Error sending password reset email: {e}")
        return False


#===============#
# Private Utils #
#===============#
async def _send_email(to_email: str, subject: str, html_content: str) -> None:
    """
    Internal method to send email via SMTP
    """

    # Run in thread pool to avoid blocking
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, _send_email_sync, to_email, subject, html_content)

def _send_email_sync(to_email: str, subject: str, html_content: str) -> None:
    """
    Synchronous email sending (runs in thread pool)
    """

    # Create message
    message = MIMEMultipart("alternative")
    message["Subject"] = subject
    message["From"] = settings.SENDER_EMAIL
    message["To"] = to_email
    
    # Attach HTML content
    message.attach(MIMEText(html_content, "html"))
    
    # Send via SMTP
    with smtplib.SMTP(settings.SMTP_SERVER, settings.SMTP_PORT) as server:
        server.starttls()
        server.login(settings.SENDER_EMAIL, settings.SENDER_PASSWORD)
        server.sendmail(settings.SENDER_EMAIL, to_email, message.as_string())
    
    print(f"Email sent to {to_email}")