"""Submission database models."""

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import Column, DateTime, func
from sqlmodel import Field, Relationship, SQLModel


class SubmissionDocument(SQLModel, table=True):
    """
    SubmissionDocument model for database storage.

    Represents individual files uploaded as part of a submission.
    """

    __tablename__ = "submission_document"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    submission_id: UUID = Field(foreign_key="submission.id", index=True)
    file_name: str = Field(max_length=255)
    file_path: str = Field(max_length=500)
    file_size: int
    content_type: str | None = Field(default=None, max_length=100)
    uploaded_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), server_default=func.now())
    )

    # Relationship
    submission: "Submission" = Relationship(back_populates="documents")


class Submission(SQLModel, table=True):
    """
    Submission model for database storage.

    Represents a submission with multiple document files.
    """

    __tablename__ = "submission"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    name: str = Field(max_length=255)
    description: str | None = Field(default=None, max_length=1000)
    pic: str | None = Field(default=None, max_length=255)
    owner_id: str = Field(foreign_key="user.id", index=True)
    created_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), server_default=func.now())
    )

    # Relationship
    documents: list["SubmissionDocument"] = Relationship(back_populates="submission")
