"""
Pydantic schemas for document processing API.

Request and response schemas for document upload, OCR, and comparison endpoints.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from app.models.document import DocumentStatus, DocumentType


class DocumentUploadResponse(BaseModel):
    """Response after uploading a document."""

    id: str
    filename: str
    file_type: DocumentType
    size_bytes: int
    status: DocumentStatus
    uploaded_at: datetime
    message: str = "Document uploaded successfully"


class DocumentProcessRequest(BaseModel):
    """Request to process a document with OCR."""

    document_id: str
    perform_ocr: bool = True
    language: Optional[str] = None  # Override default OCR language


class DocumentProcessResponse(BaseModel):
    """Response after processing a document."""

    document_id: str
    status: DocumentStatus
    ocr_text: Optional[str] = None
    ocr_confidence: Optional[float] = None
    processed_at: Optional[datetime] = None
    message: str


class DocumentComparisonRequest(BaseModel):
    """Request to compare two documents."""

    document_1_id: str = Field(..., description="First document ID")
    document_2_id: str = Field(..., description="Second document ID")
    comparison_prompt: Optional[str] = Field(
        None,
        description="Optional custom prompt for AI comparison",
    )
    use_ai_analysis: bool = Field(
        True,
        description="Whether to use AI (ChatGPT) for detailed analysis",
    )


class DocumentComparisonResponse(BaseModel):
    """Response from document comparison."""

    comparison_id: str
    document_1_id: str
    document_2_id: str
    similarity_score: float = Field(..., ge=0.0, le=1.0)
    is_consistent: bool
    differences: list[str]
    ai_analysis: Optional[str] = None
    comparison_method: str
    processing_time_seconds: float
    comparison_date: datetime


class DocumentDetailResponse(BaseModel):
    """Detailed document information."""

    id: str
    filename: str
    file_type: DocumentType
    mime_type: str
    size_bytes: int
    status: DocumentStatus
    uploaded_at: datetime
    processed_at: Optional[datetime] = None
    ocr_text: Optional[str] = None
    ocr_confidence: Optional[float] = None
    description: Optional[str] = None
    tags: list[str] = []


class DocumentListResponse(BaseModel):
    """List of documents with pagination."""

    documents: list[DocumentDetailResponse]
    total: int
    page: int
    page_size: int
