"""
File management service.

Provides high-level file operations that orchestrate CRUD and storage operations.
This service layer sits between API routes and the data/storage layers.
"""

from sqlmodel import Session

from app.core.logging import get_logger
from app.crud import file as file_crud
from app.models.file import File
from app.services.storage_service import storage_service

logger = get_logger(__name__)


def _get_file_with_permission_check(
    session: Session, file_id: str, user_id: str
) -> File | None:
    """
    Get file and verify user has permission to access it.

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


def list_user_files(session: Session, user_id: str) -> list[File]:
    """
    List all files for a user.

    Args:
        session: Database session
        user_id: User ID

    Returns:
        List of File instances
    """
    return file_crud.list_by_user(session=session, user_id=user_id)


def get_file_details(
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
    return _get_file_with_permission_check(session, file_id, user_id)


async def download_file_for_user(
    session: Session, file_id: str, user_id: str
) -> tuple[File, str] | tuple[None, None]:
    """
    Download a file for a user.

    This function is used for both downloading and processing files.

    Args:
        session: Database session
        file_id: File ID
        user_id: User ID for permission check

    Returns:
        Tuple of (File instance, temp file path) if successful, (None, None) otherwise
    """
    file_data = _get_file_with_permission_check(session, file_id, user_id)
    if not file_data:
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
    file_data = _get_file_with_permission_check(session, file_id, user_id)
    if not file_data:
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


# Alias for semantic clarity: processing a file requires downloading it first.
# Both operations perform the same action (download to temp file), but the name
# "process_file_for_user" makes the intent clearer in the processing endpoint.
process_file_for_user = download_file_for_user
