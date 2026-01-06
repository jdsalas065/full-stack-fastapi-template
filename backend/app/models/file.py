"""File database model."""

from datetime import datetime
from uuid import uuid4

from sqlmodel import Field, SQLModel


class File(SQLModel, table=True):
    """
    File model for database storage.

    Represents files uploaded by users to MinIO storage.
    Stores file metadata and references to MinIO objects.
    """

    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    user_id: str = Field(index=True, max_length=255)
    task_id: str | None = Field(default=None, index=True, max_length=255)
    filename: str = Field(max_length=255)
    file_type: str = Field(max_length=50)
    file_size: int
    object_name: str = Field(max_length=500)
    uploaded_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
