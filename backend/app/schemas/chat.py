"""Chat request and stream event schemas."""

from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """Request payload for chat streaming endpoint."""

    conversation_id: UUID | None = None
    message: str = Field(min_length=1, max_length=8000)
    model: str | None = None
    temperature: float = Field(default=0.2, ge=0.0, le=2.0)
    max_tokens: int | None = Field(default=None, gt=0, le=4096)


class ChatStreamEvent(BaseModel):
    """Server-Sent Event payload for chat token streaming."""

    event: Literal["start", "token", "heartbeat", "done", "error"]
    conversation_id: UUID | None = None
    message_id: UUID | None = None
    delta: str | None = None
    content: str | None = None
    error: str | None = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
