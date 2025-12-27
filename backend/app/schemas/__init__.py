"""
Pydantic schemas for request/response validation.

Organize schemas by domain/resource in separate files as the project grows.
Example:
    from app.schemas.common import Message
    from app.schemas.user import UserCreate, UserResponse
"""

from app.schemas.common import Message
from app.schemas.document import (
    DocumentComparisonRequest,
    DocumentComparisonResponse,
    DocumentDetailResponse,
    DocumentListResponse,
    DocumentProcessRequest,
    DocumentProcessResponse,
    DocumentUploadResponse,
)

__all__ = [
    "Message",
    "DocumentUploadResponse",
    "DocumentProcessRequest",
    "DocumentProcessResponse",
    "DocumentComparisonRequest",
    "DocumentComparisonResponse",
    "DocumentDetailResponse",
    "DocumentListResponse",
]
