"""Email utilities - stubbed out (email functionality removed)."""

import logging

logger = logging.getLogger(__name__)


def generate_password_reset_token(email: str) -> str:
    """
    Generate a password reset token (stubbed - email functionality removed).

    Args:
        email: User email address

    Returns:
        Empty string (functionality removed)
    """
    logger.warning("Password reset token generation called but email functionality is disabled")
    return ""


def verify_password_reset_token(token: str) -> str | None:
    """
    Verify a password reset token (stubbed - email functionality removed).

    Args:
        token: JWT token to verify

    Returns:
        None (functionality removed)
    """
    logger.warning("Password reset token verification called but email functionality is disabled")
    return None


def send_email(
    email_to: str,
    subject: str,
    html_content: str,
) -> None:
    """
    Send an email (stubbed - email functionality removed).

    Args:
        email_to: Recipient email address
        subject: Email subject
        html_content: HTML content of the email
    """
    logger.warning(f"Email sending called but disabled - would have sent to {email_to}: {subject}")


def send_reset_password_email(email_to: str, email: str, token: str) -> None:
    """
    Send password reset email (stubbed - email functionality removed).

    Args:
        email_to: Recipient email address
        email: User email for the reset link
        token: Password reset token
    """
    logger.warning(f"Password reset email called but disabled for {email_to}")


def send_new_account_email(email_to: str, username: str) -> None:
    """
    Send new account email (stubbed - email functionality removed).

    Args:
        email_to: Recipient email address
        username: Username for the new account
    """
    logger.warning(f"New account email called but disabled for {email_to}")

