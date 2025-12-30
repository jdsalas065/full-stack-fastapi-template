"""
File CRUD operations.

Simple in-memory storage for file metadata.
Can be replaced with database storage (SQLModel) when needed.
"""

import uuid
from datetime import datetime
from typing import Any

from app.core.logging import get_logger

logger = get_logger(__name__)


class FileCRUD:
    """CRUD operations for file metadata."""

    def __init__(self):
        """Initialize in-memory storage."""
        # In-memory storage: {file_id: file_metadata}
        self._files: dict[str, dict[str, Any]] = {}

    def create(
        self,
        user_id: str,
        filename: str,
        file_type: str,
        file_size: int,
        object_name: str,
    ) -> dict[str, Any]:
        """
        Create a new file record.

        Args:
            user_id: ID of the user uploading the file
            filename: Original filename
            file_type: Detected file type
            file_size: File size in bytes
            object_name: Object name in MinIO

        Returns:
            File metadata dictionary
        """
        file_id = str(uuid.uuid4())
        now = datetime.utcnow()

        file_data = {
            "file_id": file_id,
            "user_id": user_id,
            "filename": filename,
            "file_type": file_type,
            "file_size": file_size,
            "object_name": object_name,
            "uploaded_at": now,
            "updated_at": now,
        }

        self._files[file_id] = file_data
        logger.info(f"Created file record: {file_id}")
        return file_data

    def get(self, file_id: str) -> dict[str, Any] | None:
        """
        Get file metadata by ID.

        Args:
            file_id: File ID

        Returns:
            File metadata or None if not found
        """
        return self._files.get(file_id)

    def list_by_user(self, user_id: str) -> list[dict[str, Any]]:
        """
        List all files for a user.

        Args:
            user_id: User ID

        Returns:
            List of file metadata dictionaries
        """
        return [
            file_data
            for file_data in self._files.values()
            if file_data["user_id"] == user_id
        ]

    def delete(self, file_id: str) -> bool:
        """
        Delete file record.

        Args:
            file_id: File ID

        Returns:
            True if deleted, False if not found
        """
        if file_id in self._files:
            del self._files[file_id]
            logger.info(f"Deleted file record: {file_id}")
            return True
        return False

    def update(self, file_id: str, **kwargs: Any) -> dict[str, Any] | None:
        """
        Update file metadata.

        Args:
            file_id: File ID
            **kwargs: Fields to update

        Returns:
            Updated file metadata or None if not found
        """
        if file_id not in self._files:
            return None

        file_data = self._files[file_id]
        file_data.update(kwargs)
        file_data["updated_at"] = datetime.utcnow()
        logger.info(f"Updated file record: {file_id}")
        return file_data


# Singleton instance
file_crud = FileCRUD()
