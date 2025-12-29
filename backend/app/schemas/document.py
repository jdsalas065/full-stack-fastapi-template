"""
Document processing schemas.

Pydantic models for document submission request/response validation.
"""

from typing import Any

from pydantic import BaseModel, Field


class DocumentSubmissionRequest(BaseModel):
    """Request schema for document submission processing."""

    task_id: str = Field(..., description="Unique identifier for the document processing task")


class DocumentSubmissionResponse(BaseModel):
    """Response schema for document submission processing."""

    status: str = Field(..., description="Processing status")
    result: dict[str, Any] = Field(default_factory=dict, description="Processing results from document checks")
