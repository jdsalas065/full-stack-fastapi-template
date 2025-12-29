"""
Pydantic schemas for request/response validation.

Organize schemas by domain/resource in separate files as the project grows.
Example:
    from app.schemas.common import Message
    from app.schemas.user import UserCreate, UserResponse
"""

from app.schemas.common import Message
from app.schemas.document import (
    CompareDocumentRequest,
    CompareDocumentResponse,
    DocumentSubmissionRequest,
    DocumentSubmissionResponse,
)

__all__ = [
    "Message",
    "DocumentSubmissionRequest",
    "DocumentSubmissionResponse",
    "CompareDocumentRequest",
    "CompareDocumentResponse",
]
