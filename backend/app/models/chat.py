"""Chat conversation and message database models."""

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import Column, DateTime, Text, func
from sqlmodel import Field, Relationship, SQLModel


class ChatConversation(SQLModel, table=True):
    """Conversation model for chat sessions."""

    __tablename__ = "chat_conversation"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    owner_id: str = Field(foreign_key="user.id", index=True)
    title: str | None = Field(default=None, max_length=255)
    created_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), server_default=func.now())
    )
    updated_at: datetime = Field(
        sa_column=Column(
            DateTime(timezone=True),
            server_default=func.now(),
            onupdate=func.now(),
        )
    )

    messages: list["ChatMessage"] = Relationship(back_populates="conversation")


class ChatMessage(SQLModel, table=True):
    """Message model for conversation turns."""

    __tablename__ = "chat_message"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    conversation_id: UUID = Field(foreign_key="chat_conversation.id", index=True)
    role: str = Field(max_length=20, index=True)
    content: str = Field(sa_column=Column(Text, nullable=False))
    status: str = Field(default="completed", max_length=20, index=True)
    token_count: int = Field(default=0)
    created_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), server_default=func.now())
    )

    conversation: ChatConversation = Relationship(back_populates="messages")
