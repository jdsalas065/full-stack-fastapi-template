"""Email utilities for password reset and notifications."""

import logging
from datetime import timedelta

import jwt

from app.core.config import settings
from app.core.security import ALGORITHM

logger = logging.getLogger(__name__)


def generate_password_reset_token(email: str) -> str:
    """
    Generate a password reset token.

    Args:
        email: User email address

    Returns:
        JWT token for password reset
    """
    delta = timedelta(hours=settings.EMAIL_RESET_TOKEN_EXPIRE_HOURS)
    from app.core.security import create_access_token

    return create_access_token(subject=email, expires_delta=delta)


def verify_password_reset_token(token: str) -> str | None:
    """
    Verify a password reset token.

    Args:
        token: JWT token to verify

    Returns:
        Email address from token if valid, None otherwise
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        return email
    except jwt.PyJWTError:
        return None


def send_email(
    email_to: str,
    subject: str,
    html_content: str,
) -> None:
    """
    Send an email.

    Args:
        email_to: Recipient email address
        subject: Email subject
        html_content: HTML content of the email
    """
    # Check if email is enabled
    if not settings.emails_enabled:
        logger.warning(
            f"Email not sent to {email_to} - SMTP not configured. Subject: {subject}"
        )
        return

    # Import here to avoid issues when SMTP is not configured
    import smtplib
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText

    try:
        message = MIMEMultipart()
        message["From"] = str(settings.EMAILS_FROM_EMAIL)
        message["To"] = email_to
        message["Subject"] = subject

        message.attach(MIMEText(html_content, "html"))

        smtp_host = settings.SMTP_HOST
        if not smtp_host:
            logger.error("SMTP_HOST is not configured")
            return

        if settings.SMTP_SSL:
            server = smtplib.SMTP_SSL(smtp_host, settings.SMTP_PORT)
        else:
            server = smtplib.SMTP(smtp_host, settings.SMTP_PORT)
            if settings.SMTP_TLS:
                server.starttls()

        if settings.SMTP_USER and settings.SMTP_PASSWORD:
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)

        server.send_message(message)
        server.quit()

        logger.info(f"Email sent to {email_to}")
    except Exception as e:
        logger.error(f"Failed to send email to {email_to}: {e}")


def send_reset_password_email(email_to: str, email: str, token: str) -> None:
    """
    Send password reset email.

    Args:
        email_to: Recipient email address
        email: User email for the reset link
        token: Password reset token
    """
    project_name = settings.PROJECT_NAME
    subject = f"{project_name} - Password recovery for user {email}"

    link = f"{settings.FRONTEND_HOST}/reset-password?token={token}"

    html_content = f"""
    <html>
        <body>
            <h2>{project_name} - Password Recovery</h2>
            <p>Hello,</p>
            <p>You have requested to reset your password. Click the link below to reset it:</p>
            <p><a href="{link}">Reset Password</a></p>
            <p>If you didn't request a password reset, please ignore this email.</p>
            <p>This link will expire in {settings.EMAIL_RESET_TOKEN_EXPIRE_HOURS} hours.</p>
        </body>
    </html>
    """

    send_email(email_to=email_to, subject=subject, html_content=html_content)


def send_new_account_email(email_to: str, username: str) -> None:
    """
    Send new account email.

    Args:
        email_to: Recipient email address
        username: Username for the new account
    """
    project_name = settings.PROJECT_NAME
    subject = f"{project_name} - New account for user {username}"

    html_content = f"""
    <html>
        <body>
            <h2>{project_name} - New Account Created</h2>
            <p>Hello {username},</p>
            <p>Your account has been created successfully.</p>
            <p>You can now log in to <a href="{settings.FRONTEND_HOST}">{project_name}</a>.</p>
        </body>
    </html>
    """

    send_email(email_to=email_to, subject=subject, html_content=html_content)
