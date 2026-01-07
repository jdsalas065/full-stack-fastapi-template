"""
Submission routes.

Implements submission CRUD operations:
- Create submission with multiple file uploads
- Get submission details with permission checks
"""

from uuid import UUID

from fastapi import (
    APIRouter,
    File,
    Form,
    HTTPException,
    UploadFile,
    status,
)

from app.api.dependencies import CurrentUser, SessionDep
from app.core.constants import Tags
from app.core.logging import get_logger
from app.models.submission import Submission, SubmissionDocument
from app.schemas.submission import SubmissionDocumentPublic, SubmissionPublic
from app.services.storage_service import storage_service

logger = get_logger(__name__)

router = APIRouter(prefix="/submissions", tags=[Tags.SUBMISSIONS])


@router.post(
    "/",
    response_model=SubmissionPublic,
    status_code=status.HTTP_201_CREATED,
    summary="Create submission",
    description="Create a submission with multiple file uploads.",
)
async def create_submission(
    session: SessionDep,
    current_user: CurrentUser,
    name: str = Form(...),
    description: str | None = Form(None),
    pic: str | None = Form(None),
    files: list[UploadFile] = File(...),
) -> SubmissionPublic:
    """
    Create a new submission with file uploads.

    Args:
        session: Database session
        current_user: Current authenticated user
        name: Submission name
        description: Optional description
        pic: Optional picture/image reference
        files: List of files to upload

    Returns:
        SubmissionPublic with submission details and uploaded documents
    """
    try:
        # Generate task_id
        submission = Submission(
            name=name,
            description=description,
            pic=pic,
            owner_id=current_user.id,
        )
        task_id = submission.id

        # Add submission to session (uncommitted)
        session.add(submission)
        session.flush()  # Get the ID without committing

        # Upload files and create document records
        documents: list[SubmissionDocument] = []
        try:
            for file in files:
                # Upload to MinIO
                file_metadata = await storage_service.upload_file_from_upload(task_id, file)

                # Create document record
                doc = SubmissionDocument(
                    submission_id=task_id,
                    file_name=file_metadata["file_name"],
                    file_path=file_metadata["file_path"],
                    file_size=file_metadata["file_size"],
                    content_type=file_metadata["content_type"],
                )
                session.add(doc)
                documents.append(doc)

            # Commit transaction
            session.commit()
            session.refresh(submission)

            # Build response
            return SubmissionPublic(
                id=submission.id,
                name=submission.name,
                description=submission.description,
                pic=submission.pic,
                owner_id=submission.owner_id,
                created_at=submission.created_at,
                documents=[
                    SubmissionDocumentPublic(
                        id=doc.id,
                        submission_id=doc.submission_id,
                        file_name=doc.file_name,
                        file_path=doc.file_path,
                        file_size=doc.file_size,
                        content_type=doc.content_type,
                        uploaded_at=doc.uploaded_at,
                    )
                    for doc in documents
                ],
            )

        except Exception as upload_error:
            # Rollback database changes
            session.rollback()

            # Delete uploaded files from MinIO
            try:
                await storage_service.delete_folder(task_id)
            except Exception as cleanup_error:
                logger.error(
                    f"Failed to cleanup MinIO folder {task_id}: {cleanup_error}"
                )

            raise upload_error

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating submission: {e}", exc_info=e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create submission: {str(e)}",
        )


@router.get(
    "/{id}",
    response_model=SubmissionPublic,
    summary="Get submission",
    description="Get submission details by ID.",
)
async def get_submission(
    session: SessionDep,
    current_user: CurrentUser,
    id: UUID,
) -> SubmissionPublic:
    """
    Get submission by ID.

    Args:
        session: Database session
        current_user: Current authenticated user
        id: Submission ID

    Returns:
        SubmissionPublic with submission details

    Raises:
        HTTPException: If submission not found or access denied
    """
    try:
        # Get submission from database
        submission = session.get(Submission, id)

        if not submission:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Submission not found: {id}",
            )

        # Check permission (owner or superuser)
        if submission.owner_id != current_user.id and not current_user.is_superuser:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied",
            )

        # Build response with documents
        return SubmissionPublic(
            id=submission.id,
            name=submission.name,
            description=submission.description,
            pic=submission.pic,
            owner_id=submission.owner_id,
            created_at=submission.created_at,
            documents=[
                SubmissionDocumentPublic(
                    id=doc.id,
                    submission_id=doc.submission_id,
                    file_name=doc.file_name,
                    file_path=doc.file_path,
                    file_size=doc.file_size,
                    content_type=doc.content_type,
                    uploaded_at=doc.uploaded_at,
                )
                for doc in submission.documents
            ],
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting submission: {e}", exc_info=e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get submission: {str(e)}",
        )
