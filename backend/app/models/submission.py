"""Submission database models."""

from datetime import datetime, timezone
from uuid import uuid4

from sqlmodel import Field, Relationship, SQLModel


class Submission(SQLModel, table=True):
    """
    Submission model for database storage.

    Represents a submission that can contain multiple document files.
    Acts as a container/task for organizing related documents.
    """

    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    user_id: str = Field(index=True, max_length=255)
    task_id: str = Field(unique=True, index=True, max_length=255)
    status: str = Field(default="pending", max_length=50)  # pending, processing, completed, failed
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    # Relationships
    # NOTE: cascade_delete=True will automatically delete all associated SubmissionDocuments
    # when a Submission is deleted. While convenient, this could lead to unintended data loss.
    # Consider implementing soft deletes or requiring explicit confirmation in production.
    documents: list["SubmissionDocument"] = Relationship(back_populates="submission", cascade_delete=True)


class SubmissionDocument(SQLModel, table=True):
    """
    SubmissionDocument model for database storage.

    Links submissions to uploaded files, representing the many-to-many
    relationship between submissions and files.
    """

    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    submission_id: str = Field(foreign_key="submission.id", index=True)
    file_id: str = Field(foreign_key="file.id", index=True)
    document_type: str | None = Field(default=None, max_length=50)  # e.g., "invoice", "receipt", "contract"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    # Relationships
    submission: Submission = Relationship(back_populates="documents")
