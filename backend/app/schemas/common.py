"""
Common schemas used across the application.
"""

from pydantic import BaseModel


class Message(BaseModel):
    """Generic message schema for simple responses."""

    message: str
