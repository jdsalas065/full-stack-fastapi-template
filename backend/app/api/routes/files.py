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
from pathlib import Path
from uuid import UUID

from fastapi import (
    APIRouter,
    File,
    HTTPException,
    Query,
    UploadFile,
    status,
)
from fastapi.responses import FileResponse

from app.api.dependencies import CurrentUser, SessionDep
from app.core.constants import Tags
from app.core.logging import get_logger
from app.crud import file as file_crud
from app.models.submission import Submission, SubmissionDocument
from app.schemas.file import (
    FileDeleteResponse,
    FileInfo,
    FileListResponse,
    FileProcessRequest,
    FileProcessResponse,
    FileUploadResponse,
)
from app.services.document_processor import document_processor
from app.services.file_service import (
    delete_file_for_user,
    download_file_for_user,
    get_file_details,
    list_user_files,
    process_file_for_user,
)
from app.services.minio_service import upload_file_to_minio

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
    current_user: CurrentUser,
    file: UploadFile = File(...),
    task_id: str = Query(
        ..., description="Task ID for file upload (use 'root' for root directory)"
    ),
) -> FileUploadResponse:
    """
    Upload a file to MinIO storage.

    Accepts: Excel (.xlsx, .xls), PDF (.pdf), Word (.doc, .docx),
    Images (.png, .jpg, .jpeg, .bmp, .tiff, .gif)

    Args:
        session: Database session
        current_user: Current authenticated user
        file: File to upload
        task_id: Required task ID for document processing.
                 If "root", file will be stored in root directory (superuser only).
                 Otherwise, must be a valid submission ID.

    Returns:
        FileUploadResponse with file metadata
    """
    try:
        # Validate file
        validate_file(file)

        # Validate task_id
        task_id = task_id.strip()
        if not task_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="task_id cannot be empty",
            )

        # Handle special "root" case
        if task_id == "root":
            # Only superusers can upload to root
            if not current_user.is_superuser:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Only superusers can upload to root directory",
                )

            # Upload to root (no submission record created)
            file_metadata = await upload_file_to_minio(task_id, file)

            # Create file record in database
            file_data = file_crud.create(
                session=session,
                user_id=current_user.id,
                filename=file_metadata["file_name"],
                file_type=document_processor.detect_file_type(
                    file_metadata["file_name"]
                ),
                file_size=file_metadata["file_size"],
                object_name=file_metadata["file_path"],
                task_id="root",
            )

            return FileUploadResponse(
                file_id=file_data.id,
                filename=file_data.filename,
                file_type=file_data.file_type,
                file_size=file_data.file_size,
                object_name=file_data.object_name,
                task_id=file_data.task_id,
                uploaded_at=file_data.uploaded_at,
            )

        # Handle submission task_id
        try:
            submission_id = UUID(task_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid task_id format. Must be a valid UUID or 'root'",
            )

        # Check if submission exists
        submission = session.get(Submission, submission_id)
        if not submission:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Submission not found: {task_id}",
            )

        # Check permission (owner or superuser)
        if submission.owner_id != current_user.id and not current_user.is_superuser:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied. You don't have permission to upload to this submission.",
            )

        # Upload file to MinIO
        file_metadata = await upload_file_to_minio(task_id, file)

        # Create SubmissionDocument record
        doc = SubmissionDocument(
            submission_id=submission_id,
            file_name=file_metadata["file_name"],
            file_path=file_metadata["file_path"],
            file_size=file_metadata["file_size"],
            content_type=file_metadata["content_type"],
        )
        session.add(doc)

        # Also create File record for backward compatibility
        file_data = file_crud.create(
            session=session,
            user_id=current_user.id,
            filename=file_metadata["file_name"],
            file_type=document_processor.detect_file_type(file_metadata["file_name"]),
            file_size=file_metadata["file_size"],
            object_name=file_metadata["file_path"],
            task_id=task_id,
        )

        session.commit()

        return FileUploadResponse(
            file_id=file_data.id,
            filename=file_data.filename,
            file_type=file_data.file_type,
            file_size=file_data.file_size,
            object_name=file_data.object_name,
            task_id=file_data.task_id,
            uploaded_at=file_data.uploaded_at,
        )

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
async def list_files(
    session: SessionDep, current_user: CurrentUser
) -> FileListResponse:
    """
    List all files for the current user.

    Returns:
        FileListResponse with list of files
    """
    try:
        files = list_user_files(session=session, user_id=current_user.id)

        file_infos = [
            FileInfo(
                file_id=f.id,
                user_id=f.user_id,
                filename=f.filename,
                file_type=f.file_type,
                file_size=f.file_size,
                object_name=f.object_name,
                task_id=f.task_id,
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
async def get_file(
    file_id: str, session: SessionDep, current_user: CurrentUser
) -> FileInfo:
    """
    Get file details.

    Args:
        file_id: File ID

    Returns:
        FileInfo with file details
    """
    try:
        file_data = get_file_details(
            session=session, file_id=file_id, user_id=current_user.id
        )
        if not file_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"File not found: {file_id}",
            )

        return FileInfo(
            file_id=file_data.id,
            user_id=file_data.user_id,
            filename=file_data.filename,
            file_type=file_data.file_type,
            file_size=file_data.file_size,
            object_name=file_data.object_name,
            task_id=file_data.task_id,
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
async def download_file(
    file_id: str, session: SessionDep, current_user: CurrentUser
) -> FileResponse:
    """
    Download a file.

    Args:
        file_id: File ID

    Returns:
        FileResponse with file content
    """
    temp_path = None
    try:
        file_data, temp_path = await download_file_for_user(
            session=session, file_id=file_id, user_id=current_user.id
        )
        if not file_data or not temp_path:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"File not found: {file_id}",
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
async def delete_file(
    file_id: str, session: SessionDep, current_user: CurrentUser
) -> FileDeleteResponse:
    """
    Delete a file.

    Args:
        file_id: File ID

    Returns:
        FileDeleteResponse with deletion status
    """
    try:
        success = await delete_file_for_user(
            session=session, file_id=file_id, user_id=current_user.id
        )
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"File not found: {file_id}",
            )

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
    current_user: CurrentUser,
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
        file_data, temp_path = await process_file_for_user(
            session=session, file_id=file_id, user_id=current_user.id
        )
        if not file_data or not temp_path:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"File not found: {file_id}",
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
