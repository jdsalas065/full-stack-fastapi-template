"""Submission schemas for API requests and responses."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class SubmissionDocumentPublic(BaseModel):
    """Public schema for submission document."""

    id: UUID
    submission_id: UUID
    file_name: str
    file_path: str
    file_size: int
    content_type: str | None
    uploaded_at: datetime


class SubmissionPublic(BaseModel):
    """Public schema for submission."""

    id: UUID
    name: str
    description: str | None
    pic: str | None
    owner_id: str
    created_at: datetime
    documents: list[SubmissionDocumentPublic]


class SubmissionCreate(BaseModel):
    """Schema for creating a submission."""

    name: str
    description: str | None = None
    pic: str | None = None
