"""
Database models for document management.

Models for storing document metadata, processing results, and comparison history.
"""

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel


class DocumentStatus(str, Enum):
    """Status of document processing."""

    UPLOADED = "uploaded"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class DocumentType(str, Enum):
    """Type of document."""

    PDF = "pdf"
    IMAGE = "image"
    WORD = "word"
    OTHER = "other"


class Document(BaseModel):
    """
    Document model for storing document metadata.
    
    This would typically extend SQLModel for database persistence.
    For now, using Pydantic BaseModel as a placeholder.
    """

    id: Optional[str] = None
    filename: str
    file_path: str
    file_type: DocumentType
    mime_type: str
    size_bytes: int
    status: DocumentStatus = DocumentStatus.UPLOADED
    uploaded_at: datetime
    processed_at: Optional[datetime] = None
    
    # OCR Results
    ocr_text: Optional[str] = None
    ocr_confidence: Optional[float] = None
    
    # Metadata
    user_id: Optional[str] = None
    description: Optional[str] = None
    tags: list[str] = []


class DocumentComparison(BaseModel):
    """
    Model for storing document comparison results.
    
    Stores the results of comparing two documents for consistency.
    """

    id: Optional[str] = None
    document_1_id: str
    document_2_id: str
    comparison_date: datetime
    
    # Comparison Results
    similarity_score: float  # 0.0 to 1.0
    is_consistent: bool
    differences: list[str] = []
    ai_analysis: Optional[str] = None
    
    # Metadata
    comparison_method: str  # e.g., "openai_gpt4", "text_similarity", "hybrid"
    processing_time_seconds: Optional[float] = None
