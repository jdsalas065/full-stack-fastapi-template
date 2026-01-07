"""Submission schemas for API validation."""

from datetime import datetime

from pydantic import BaseModel, Field


# Submission schemas
class SubmissionCreate(BaseModel):
    """Schema for creating a new submission."""

    task_id: str = Field(..., description="Unique task identifier")
    status: str = Field(default="pending", description="Submission status")


class SubmissionUpdate(BaseModel):
    """Schema for updating a submission."""

    status: str | None = Field(None, description="Submission status")


class SubmissionPublic(BaseModel):
    """Schema for submission response."""

    id: str
    user_id: str
    task_id: str
    status: str
    created_at: datetime
    updated_at: datetime


class SubmissionListResponse(BaseModel):
    """Schema for submission list response."""

    submissions: list[SubmissionPublic]
    total: int


# SubmissionDocument schemas
class SubmissionDocumentCreate(BaseModel):
    """Schema for creating a submission document link."""

    submission_id: str
    file_id: str
    document_type: str | None = None


class SubmissionDocumentPublic(BaseModel):
    """Schema for submission document response."""

    id: str
    submission_id: str
    file_id: str
    document_type: str | None
    created_at: datetime


class SubmissionWithDocuments(SubmissionPublic):
    """Schema for submission with documents."""

    documents: list[SubmissionDocumentPublic] = []
