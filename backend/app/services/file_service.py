"""
File management service.

Provides high-level file operations that orchestrate CRUD and storage operations.
This service layer sits between API routes and the data/storage layers.
"""

from uuid import UUID

from sqlmodel import Session

from app.core.logging import get_logger
from app.crud import file as file_crud
from app.models.file import File
from app.services.storage_service import storage_service

logger = get_logger(__name__)


async def list_user_files(session: Session, user_id: str) -> list[File]:
    """
    List all files for a user.

    Args:
        session: Database session
        user_id: User ID

    Returns:
        List of File instances
    """
    return file_crud.list_by_user(session=session, user_id=user_id)


async def get_file_details(
    session: Session, file_id: str, user_id: str
) -> File | None:
    """
    Get file details for a user.

    Args:
        session: Database session
        file_id: File ID
        user_id: User ID for permission check

    Returns:
        File instance if found and user has access, None otherwise
    """
    file_data = file_crud.get(session=session, file_id=file_id)
    if not file_data:
        return None

    # Verify user owns the file
    if file_data.user_id != user_id:
        return None

    return file_data


async def download_file_for_user(
    session: Session, file_id: str, user_id: str
) -> tuple[File, str] | tuple[None, None]:
    """
    Download a file for a user.

    Args:
        session: Database session
        file_id: File ID
        user_id: User ID for permission check

    Returns:
        Tuple of (File instance, temp file path) if successful, (None, None) otherwise
    """
    file_data = file_crud.get(session=session, file_id=file_id)
    if not file_data:
        return None, None

    # Verify user owns the file
    if file_data.user_id != user_id:
        return None, None

    # Download from MinIO to temp file
    try:
        temp_path = await storage_service.download_file_to_temp(file_data.object_name)
        return file_data, temp_path
    except Exception as e:
        logger.error(f"Error downloading file {file_id}: {e}")
        return None, None


async def delete_file_for_user(
    session: Session, file_id: str, user_id: str
) -> bool:
    """
    Delete a file for a user.

    Args:
        session: Database session
        file_id: File ID
        user_id: User ID for permission check

    Returns:
        True if deleted successfully, False otherwise
    """
    file_data = file_crud.get(session=session, file_id=file_id)
    if not file_data:
        return False

    # Verify user owns the file
    if file_data.user_id != user_id:
        return False

    # Delete from MinIO
    try:
        await storage_service.delete_file(file_data.object_name)
    except Exception as e:
        logger.error(f"Error deleting file from storage {file_id}: {e}")
        raise

    # Delete from database
    file_crud.delete(session=session, file_id=file_id)
    return True


async def process_file_for_user(
    session: Session, file_id: str, user_id: str
) -> tuple[File, str] | tuple[None, None]:
    """
    Prepare a file for processing by downloading it.

    Args:
        session: Database session
        file_id: File ID
        user_id: User ID for permission check

    Returns:
        Tuple of (File instance, temp file path) if successful, (None, None) otherwise
    """
    file_data = file_crud.get(session=session, file_id=file_id)
    if not file_data:
        return None, None

    # Verify user owns the file
    if file_data.user_id != user_id:
        return None, None

    # Download file to temp for processing
    try:
        temp_path = await storage_service.download_file_to_temp(file_data.object_name)
        return file_data, temp_path
    except Exception as e:
        logger.error(f"Error downloading file for processing {file_id}: {e}")
        return None, None
