import uuid

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from app.api.deps import CurrentUser, SessionDep
from app.models import (
    Message,
    Submission,
    SubmissionDocument,
    SubmissionDocumentPublic,
)
from app.services.minio import get_minio_service

router = APIRouter(prefix="/files", tags=["files"])


@router.post("/upload", response_model=SubmissionDocumentPublic)
async def upload_file(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    file: UploadFile = File(...),
    submission_id: str = Form(...),
) -> SubmissionDocumentPublic:
    """
    Upload a file to an existing submission.

    - submission_id: UUID of the submission to upload to
    """
    # Pre-generate UUID for atomic operations
    document_id = uuid.uuid4()

    # Read file data
    file_data = await file.read()
    if not file_data:
        raise HTTPException(status_code=400, detail="Empty file")

    # Parse and validate submission ID
    try:
        submission_uuid = uuid.UUID(submission_id)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Invalid submission_id format. Must be a valid UUID",
        )

    # Validate submission exists
    submission = session.get(Submission, submission_uuid)
    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")

    # Check permissions
    if not current_user.is_superuser and submission.owner_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Not enough permissions to upload to this submission",
        )

    # Upload file with rollback on error
    uploaded_file_path = None
    minio_service = get_minio_service()
    try:
        # Upload to MinIO
        file_path, file_size = minio_service.upload_file(
            file_data,
            file.filename or "unnamed",
            file.content_type or "application/octet-stream",
            folder=str(submission_uuid),
        )
        uploaded_file_path = file_path

        # Create document record in database
        document = SubmissionDocument(
            id=document_id,
            submission_id=submission_uuid,
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
        if uploaded_file_path:
            try:
                minio_service.delete_file(uploaded_file_path)
            except Exception:
                # Log the error but continue with the original exception
                # In production, use proper logging
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
        minio_service = get_minio_service()
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

    minio_service = get_minio_service()
    try:
        # Delete from MinIO
        minio_service.delete_file(document.file_path)
    except Exception:
        # Continue with DB deletion even if MinIO deletion fails
        # In production, use proper logging
        pass

    # Delete from database
    session.delete(document)
    session.commit()

    return Message(message="File deleted successfully")
