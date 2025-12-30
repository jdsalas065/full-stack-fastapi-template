"""
Document processing schemas.

Pydantic models for document submission request/response validation.
"""

from typing import Any

from pydantic import BaseModel, Field


class DocumentSubmissionRequest(BaseModel):
    """Request schema for document submission processing."""

    task_id: str = Field(
        ..., description="Unique identifier for the document processing task"
    )


class DocumentSubmissionResponse(BaseModel):
    """Response schema for document submission processing."""

    status: str = Field(..., description="Processing status")
    result: dict[str, Any] = Field(
        default_factory=dict, description="Processing results from document checks"
    )


class CompareDocumentRequest(BaseModel):
    """Request schema for document comparison."""

    task_id: str = Field(..., description="Unique identifier for the task")
    excel_file_name: str = Field(..., description="Name of the Excel file to compare")
    pdf_file_name: str = Field(..., description="Name of the PDF file to compare")


class CompareDocumentResponse(BaseModel):
    """Response schema for document comparison."""

    status: str = Field(..., description="Comparison status")
    result: dict[str, Any] = Field(
        default_factory=dict, description="Comparison results"
    )
