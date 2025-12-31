"""
File CRUD operations.

Database-backed CRUD operations for file metadata.
"""

from datetime import datetime
from typing import Any

from sqlmodel import Session, select

from app.core.logging import get_logger
from app.models.file import File

logger = get_logger(__name__)


def create(
    *,
    session: Session,
    user_id: str,
    filename: str,
    file_type: str,
    file_size: int,
    object_name: str,
) -> File:
    """
    Create a new file record.

    Args:
        session: Database session
        user_id: ID of the user uploading the file
        filename: Original filename
        file_type: Detected file type
        file_size: File size in bytes
        object_name: Object name in MinIO

    Returns:
        File instance
    """
    db_obj = File(
        user_id=user_id,
        filename=filename,
        file_type=file_type,
        file_size=file_size,
        object_name=object_name,
    )
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    logger.info(f"Created file record: {db_obj.id}")
    return db_obj


def get(*, session: Session, file_id: str) -> File | None:
    """
    Get file metadata by ID.

    Args:
        session: Database session
        file_id: File ID

    Returns:
        File instance if found, None otherwise
    """
    return session.get(File, file_id)


def list_by_user(*, session: Session, user_id: str) -> list[File]:
    """
    List all files for a user.

    Args:
        session: Database session
        user_id: User ID

    Returns:
        List of File instances
    """
    statement = select(File).where(File.user_id == user_id)
    return list(session.exec(statement).all())


def delete(*, session: Session, file_id: str) -> bool:
    """
    Delete file record.

    Args:
        session: Database session
        file_id: File ID

    Returns:
        True if deleted, False if not found
    """
    file = session.get(File, file_id)
    if file:
        session.delete(file)
        session.commit()
        logger.info(f"Deleted file record: {file_id}")
        return True
    return False


def update(*, session: Session, file_id: str, **kwargs: Any) -> File | None:
    """
    Update file metadata.

    Args:
        session: Database session
        file_id: File ID
        **kwargs: Fields to update

    Returns:
        Updated File instance or None if not found
    """
    file = session.get(File, file_id)
    if not file:
        return None

    for key, value in kwargs.items():
        setattr(file, key, value)

    file.updated_at = datetime.utcnow()
    session.add(file)
    session.commit()
    session.refresh(file)
    logger.info(f"Updated file record: {file_id}")
    return file

