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
from app.schemas.submission import (
    SubmissionCreate,
    SubmissionDocumentCreate,
    SubmissionDocumentPublic,
    SubmissionListResponse,
    SubmissionPublic,
    SubmissionUpdate,
    SubmissionWithDocuments,
)

__all__ = [
    "Message",
    "DocumentSubmissionRequest",
    "DocumentSubmissionResponse",
    "CompareDocumentRequest",
    "CompareDocumentResponse",
    "SubmissionCreate",
    "SubmissionUpdate",
    "SubmissionPublic",
    "SubmissionListResponse",
    "SubmissionWithDocuments",
    "SubmissionDocumentCreate",
    "SubmissionDocumentPublic",
]
