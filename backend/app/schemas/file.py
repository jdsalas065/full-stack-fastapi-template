"""
File management schemas.

Pydantic models for file upload and management request/response validation.
"""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class FileUploadResponse(BaseModel):
    """Response schema for file upload."""

    file_id: str = Field(..., description="Unique identifier for the uploaded file")
    filename: str = Field(..., description="Original filename")
    file_type: str = Field(..., description="Detected file type")
    file_size: int = Field(..., description="File size in bytes")
    object_name: str = Field(..., description="Object name in MinIO storage")
    uploaded_at: datetime = Field(..., description="Upload timestamp")


class FileInfo(BaseModel):
    """File information schema."""

    file_id: str = Field(..., description="Unique identifier for the file")
    user_id: str = Field(..., description="User ID who uploaded the file")
    filename: str = Field(..., description="Original filename")
    file_type: str = Field(..., description="File type")
    file_size: int = Field(..., description="File size in bytes")
    object_name: str = Field(..., description="Object name in MinIO storage")
    uploaded_at: datetime = Field(..., description="Upload timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")


class FileListResponse(BaseModel):
    """Response schema for file listing."""

    files: list[FileInfo] = Field(default_factory=list, description="List of files")
    total: int = Field(..., description="Total number of files")


class FileDeleteResponse(BaseModel):
    """Response schema for file deletion."""

    message: str = Field(..., description="Deletion status message")
    file_id: str = Field(..., description="Deleted file ID")


class FileProcessRequest(BaseModel):
    """Request schema for file processing."""

    file_id: str = Field(..., description="File ID to process")
    extract_fields: bool = Field(
        default=True, description="Whether to extract fields from the document"
    )


class FileProcessResponse(BaseModel):
    """Response schema for file processing."""

    status: str = Field(..., description="Processing status")
    file_id: str = Field(..., description="File ID that was processed")
    result: dict[str, Any] = Field(
        default_factory=dict, description="Processing results"
    )
