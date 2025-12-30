"""
File management routes.

Implements file CRUD operations:
- Upload files to MinIO
- List user files
- Get file details
- Download files
- Delete files
- Process files (extract content)
"""

import os
import tempfile
from pathlib import Path

from fastapi import (
    APIRouter,
    File,
    HTTPException,
    UploadFile,
    status,
)
from fastapi.responses import FileResponse

from app.api.dependencies import SessionDep
from app.core.constants import Tags
from app.core.logging import get_logger
from app.crud import file as file_crud
from app.schemas.file import (
    FileDeleteResponse,
    FileInfo,
    FileListResponse,
    FileProcessRequest,
    FileProcessResponse,
    FileUploadResponse,
)
from app.services.document_processor import document_processor
from app.services.storage_service import storage_service

logger = get_logger(__name__)

router = APIRouter(prefix="/files", tags=[Tags.FILES])

# Supported file types
SUPPORTED_EXTENSIONS = {
    ".xlsx",
    ".xls",
    ".pdf",
    ".doc",
    ".docx",
    ".png",
    ".jpg",
    ".jpeg",
    ".bmp",
    ".tiff",
    ".gif",
}

# Max file size: 50MB
MAX_FILE_SIZE = 50 * 1024 * 1024


def get_current_user_id() -> str:
    """
    Get current user ID.

    TODO: Replace with actual authentication.
    For now, return a default user ID.
    """
    return "default-user"


def validate_file(file: UploadFile) -> None:
    """
    Validate uploaded file.

    Args:
        file: Uploaded file

    Raises:
        HTTPException: If file validation fails
    """
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Filename is required",
        )

    ext = Path(file.filename).suffix.lower()
    if ext not in SUPPORTED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file type: {ext}. Supported: {', '.join(SUPPORTED_EXTENSIONS)}",
        )


@router.post(
    "/upload",
    response_model=FileUploadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload file",
    description="Upload a document file (Excel, PDF, docs, images) to MinIO storage.",
)
async def upload_file(
    session: SessionDep,
    file: UploadFile = File(...),
) -> FileUploadResponse:
    """
    Upload a file to MinIO storage.

    Accepts: Excel (.xlsx, .xls), PDF (.pdf), Word (.doc, .docx),
    Images (.png, .jpg, .jpeg, .bmp, .tiff, .gif)

    Returns:
        FileUploadResponse with file metadata
    """
    try:
        # Get current user
        user_id = get_current_user_id()

        # Validate file
        validate_file(file)

        # Read file content
        content = await file.read()
        file_size = len(content)

        if file_size > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File too large. Max size: {MAX_FILE_SIZE / 1024 / 1024}MB",
            )

        # Save to temp file first
        temp_fd, temp_path = tempfile.mkstemp(suffix=Path(file.filename).suffix)
        try:
            with os.fdopen(temp_fd, "wb") as f:
                f.write(content)

            # Detect file type
            file_type = document_processor.detect_file_type(file.filename)

            # Generate object name
            object_name = f"{user_id}/{file.filename}"

            # Upload to MinIO
            await storage_service.upload_file(
                temp_path,
                object_name,
                content_type=file.content_type,
            )

            # Create file record in database
            file_data = file_crud.create(
                session=session,
                user_id=user_id,
                filename=file.filename,
                file_type=file_type,
                file_size=file_size,
                object_name=object_name,
            )

            return FileUploadResponse(
                file_id=file_data.id,
                filename=file_data.filename,
                file_type=file_data.file_type,
                file_size=file_data.file_size,
                object_name=file_data.object_name,
                uploaded_at=file_data.uploaded_at,
            )

        finally:
            # Clean up temp file
            try:
                os.unlink(temp_path)
            except Exception as e:
                logger.warning(f"Failed to delete temp file {temp_path}: {e}")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading file: {e}", exc_info=e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload file: {str(e)}",
        )


@router.get(
    "",
    response_model=FileListResponse,
    summary="List files",
    description="List all files uploaded by the current user.",
)
async def list_files(session: SessionDep) -> FileListResponse:
    """
    List all files for the current user.

    Returns:
        FileListResponse with list of files
    """
    try:
        user_id = get_current_user_id()
        files = file_crud.list_by_user(session=session, user_id=user_id)

        file_infos = [
            FileInfo(
                file_id=f.id,
                user_id=f.user_id,
                filename=f.filename,
                file_type=f.file_type,
                file_size=f.file_size,
                object_name=f.object_name,
                uploaded_at=f.uploaded_at,
                updated_at=f.updated_at,
            )
            for f in files
        ]

        return FileListResponse(files=file_infos, total=len(file_infos))

    except Exception as e:
        logger.error(f"Error listing files: {e}", exc_info=e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list files: {str(e)}",
        )


@router.get(
    "/{file_id}",
    response_model=FileInfo,
    summary="Get file details",
    description="Get details of a specific file.",
)
async def get_file(file_id: str, session: SessionDep) -> FileInfo:
    """
    Get file details.

    Args:
        file_id: File ID

    Returns:
        FileInfo with file details
    """
    try:
        file_data = file_crud.get(session=session, file_id=file_id)
        if not file_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"File not found: {file_id}",
            )

        # Verify user owns the file
        user_id = get_current_user_id()
        if file_data.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied",
            )

        return FileInfo(
            file_id=file_data.id,
            user_id=file_data.user_id,
            filename=file_data.filename,
            file_type=file_data.file_type,
            file_size=file_data.file_size,
            object_name=file_data.object_name,
            uploaded_at=file_data.uploaded_at,
            updated_at=file_data.updated_at,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting file: {e}", exc_info=e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get file: {str(e)}",
        )


@router.get(
    "/{file_id}/download",
    summary="Download file",
    description="Download a file from storage.",
)
async def download_file(file_id: str, session: SessionDep) -> FileResponse:
    """
    Download a file.

    Args:
        file_id: File ID

    Returns:
        FileResponse with file content
    """
    temp_path = None
    try:
        file_data = file_crud.get(session=session, file_id=file_id)
        if not file_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"File not found: {file_id}",
            )

        # Verify user owns the file
        user_id = get_current_user_id()
        if file_data.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied",
            )

        # Download from MinIO to temp file
        temp_path = await storage_service.download_file_to_temp(
            file_data.object_name
        )

        return FileResponse(
            path=temp_path,
            filename=file_data.filename,
            media_type="application/octet-stream",
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error downloading file: {e}", exc_info=e)
        # Clean up temp file on error
        if temp_path:
            try:
                os.unlink(temp_path)
            except Exception:
                pass
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to download file: {str(e)}",
        )


@router.delete(
    "/{file_id}",
    response_model=FileDeleteResponse,
    summary="Delete file",
    description="Delete a file from storage.",
)
async def delete_file(file_id: str, session: SessionDep) -> FileDeleteResponse:
    """
    Delete a file.

    Args:
        file_id: File ID

    Returns:
        FileDeleteResponse with deletion status
    """
    try:
        file_data = file_crud.get(session=session, file_id=file_id)
        if not file_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"File not found: {file_id}",
            )

        # Verify user owns the file
        user_id = get_current_user_id()
        if file_data.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied",
            )

        # Delete from MinIO
        await storage_service.delete_file(file_data.object_name)

        # Delete from database
        file_crud.delete(session=session, file_id=file_id)

        return FileDeleteResponse(
            message="File deleted successfully",
            file_id=file_id,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting file: {e}", exc_info=e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete file: {str(e)}",
        )


@router.post(
    "/{file_id}/process",
    response_model=FileProcessResponse,
    summary="Process file",
    description="Process file to extract content and fields.",
)
async def process_file(
    file_id: str,
    session: SessionDep,
    payload: FileProcessRequest | None = None,  # noqa: ARG001
) -> FileProcessResponse:
    """
    Process a file to extract content and fields.

    Args:
        file_id: File ID
        payload: Optional processing options

    Returns:
        FileProcessResponse with processing results
    """
    temp_path = None
    try:
        file_data = file_crud.get(session=session, file_id=file_id)
        if not file_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"File not found: {file_id}",
            )

        # Verify user owns the file
        user_id = get_current_user_id()
        if file_data.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied",
            )

        # Download file to temp
        temp_path = await storage_service.download_file_to_temp(
            file_data.object_name
        )

        # Process file
        result = await document_processor.process_file_from_path(
            temp_path,
            file_data.filename,
            file_data.file_type,
        )

        return FileProcessResponse(
            status="processed",
            file_id=file_id,
            result=result,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing file: {e}", exc_info=e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process file: {str(e)}",
        )
    finally:
        # Clean up temp file
        if temp_path:
            try:
                os.unlink(temp_path)
            except Exception as e:
                logger.warning(f"Failed to delete temp file {temp_path}: {e}")
