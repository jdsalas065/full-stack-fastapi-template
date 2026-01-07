import uuid

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from app.api.deps import CurrentUser, SessionDep
from app.models import (
    Message,
    Submission,
    SubmissionDocument,
    SubmissionDocumentPublic,
)
from app.services.minio import minio_service

router = APIRouter(prefix="/files", tags=["files"])


@router.post("/upload", response_model=SubmissionDocumentPublic)
async def upload_file(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    file: UploadFile = File(...),
    task_id: str = Form(...),
) -> SubmissionDocumentPublic:
    """
    Upload a file to a submission or root folder (admin only).

    - task_id="root": Upload to root folder (admin only)
    - task_id=<uuid>: Upload to existing submission with validation
    """
    # Pre-generate UUID for atomic operations
    document_id = uuid.uuid4()

    # Read file data
    file_data = await file.read()
    if not file_data:
        raise HTTPException(status_code=400, detail="Empty file")

    # Handle "root" folder upload (admin only)
    if task_id == "root":
        if not current_user.is_superuser:
            raise HTTPException(
                status_code=403,
                detail="Only administrators can upload to root folder",
            )

        try:
            # Upload to MinIO
            file_path, file_size = minio_service.upload_file(
                file_data,
                file.filename or "unnamed",
                file.content_type or "application/octet-stream",
                folder="root",
            )

            # Create document record without submission_id
            # Note: This requires modifying the SubmissionDocument model to make submission_id nullable
            # For now, we'll raise an error as the schema doesn't support it
            raise HTTPException(
                status_code=501,
                detail="Root folder upload not fully implemented - requires schema changes",
            )
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

    # Handle submission upload
    try:
        submission_id = uuid.UUID(task_id)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Invalid task_id format. Must be a valid UUID or 'root'",
        )

    # Validate submission exists
    submission = session.get(Submission, submission_id)
    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")

    # Check permissions
    if not current_user.is_superuser and submission.owner_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Not enough permissions to upload to this submission",
        )

    # Upload file with rollback on error
    try:
        # Upload to MinIO
        file_path, file_size = minio_service.upload_file(
            file_data,
            file.filename or "unnamed",
            file.content_type or "application/octet-stream",
            folder=str(submission_id),
        )

        # Create document record in database
        document = SubmissionDocument(
            id=document_id,
            submission_id=submission_id,
            filename=file.filename or "unnamed",
            file_path=file_path,
            file_size=file_size,
            content_type=file.content_type or "application/octet-stream",
        )
        session.add(document)
        session.commit()
        session.refresh(document)

        return document
    except Exception as e:
        # Rollback: delete file from MinIO if it was uploaded
        try:
            if "file_path" in locals():
                minio_service.delete_file(file_path)
        except Exception:
            pass

        # Rollback database changes
        session.rollback()

        raise HTTPException(
            status_code=500,
            detail=f"Upload failed: {str(e)}",
        )


@router.get("/download/{document_id}")
def get_download_url(
    session: SessionDep,
    current_user: CurrentUser,
    document_id: uuid.UUID,
) -> dict[str, str]:
    """
    Get a presigned URL for downloading a file.
    """
    document = session.get(SubmissionDocument, document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    # Check permissions
    submission = session.get(Submission, document.submission_id)
    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")

    if not current_user.is_superuser and submission.owner_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Not enough permissions to download this file",
        )

    try:
        url = minio_service.get_presigned_url(document.file_path)
        return {"download_url": url}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate download URL: {str(e)}",
        )


@router.delete("/{document_id}")
def delete_file(
    session: SessionDep,
    current_user: CurrentUser,
    document_id: uuid.UUID,
) -> Message:
    """
    Delete a file.
    """
    document = session.get(SubmissionDocument, document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    # Check permissions
    submission = session.get(Submission, document.submission_id)
    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")

    if not current_user.is_superuser and submission.owner_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Not enough permissions to delete this file",
        )

    try:
        # Delete from MinIO
        minio_service.delete_file(document.file_path)
    except Exception:
        # Continue with DB deletion even if MinIO deletion fails
        pass

    # Delete from database
    session.delete(document)
    session.commit()

    return Message(message="File deleted successfully")
