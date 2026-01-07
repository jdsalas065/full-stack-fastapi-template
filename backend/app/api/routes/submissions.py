"""
Submission management routes.

Implements submission CRUD operations:
- Create submission
- List user submissions
- Get submission details
- Update submission
- Delete submission
"""

from fastapi import APIRouter, HTTPException, status

from app.api.dependencies import SessionDep
from app.core.constants import Tags
from app.core.logging import get_logger
from app.crud import submission as submission_crud
from app.schemas.submission import (
    SubmissionCreate,
    SubmissionDocumentPublic,
    SubmissionListResponse,
    SubmissionPublic,
    SubmissionUpdate,
    SubmissionWithDocuments,
)

logger = get_logger(__name__)

router = APIRouter(prefix="/submissions", tags=[Tags.SUBMISSIONS])


def get_current_user_id() -> str:
    """
    Get current user ID.

    SECURITY WARNING: This is a placeholder implementation for development/testing.
    In production, this MUST be replaced with proper authentication that:
    1. Validates user credentials (JWT token, session, OAuth, etc.)
    2. Returns the actual authenticated user's ID
    3. Handles unauthorized access appropriately

    Current implementation returns a hardcoded value which means:
    - All operations are attributed to the same user
    - No user isolation or access control
    - DO NOT use in production!

    TODO: Replace with actual authentication (e.g., from JWT token in Authorization header)
    """
    return "default-user"


@router.post(
    "",
    response_model=SubmissionPublic,
    status_code=status.HTTP_201_CREATED,
    summary="Create submission",
    description="Create a new submission with a unique task_id.",
)
async def create_submission(
    session: SessionDep,
    submission_in: SubmissionCreate,
) -> SubmissionPublic:
    """
    Create a new submission.

    Args:
        session: Database session
        submission_in: Submission creation data

    Returns:
        SubmissionPublic with submission details
    """
    try:
        user_id = get_current_user_id()

        # Check if task_id already exists
        existing = submission_crud.get_submission_by_task_id(
            session=session, task_id=submission_in.task_id
        )
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Submission with task_id '{submission_in.task_id}' already exists",
            )

        # Create submission
        submission = submission_crud.create_submission(
            session=session,
            user_id=user_id,
            task_id=submission_in.task_id,
            status=submission_in.status,
        )

        return SubmissionPublic(
            id=submission.id,
            user_id=submission.user_id,
            task_id=submission.task_id,
            status=submission.status,
            created_at=submission.created_at,
            updated_at=submission.updated_at,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating submission: {e}", exc_info=e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create submission: {str(e)}",
        )


@router.get(
    "",
    response_model=SubmissionListResponse,
    summary="List submissions",
    description="List all submissions for the current user.",
)
async def list_submissions(session: SessionDep) -> SubmissionListResponse:
    """
    List all submissions for the current user.

    Returns:
        SubmissionListResponse with list of submissions
    """
    try:
        user_id = get_current_user_id()
        submissions = submission_crud.list_submissions_by_user(
            session=session, user_id=user_id
        )

        submission_list = [
            SubmissionPublic(
                id=s.id,
                user_id=s.user_id,
                task_id=s.task_id,
                status=s.status,
                created_at=s.created_at,
                updated_at=s.updated_at,
            )
            for s in submissions
        ]

        return SubmissionListResponse(
            submissions=submission_list, total=len(submission_list)
        )

    except Exception as e:
        logger.error(f"Error listing submissions: {e}", exc_info=e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list submissions: {str(e)}",
        )


@router.get(
    "/{submission_id}",
    response_model=SubmissionWithDocuments,
    summary="Get submission",
    description="Get details of a specific submission with its documents.",
)
async def get_submission(
    submission_id: str, session: SessionDep
) -> SubmissionWithDocuments:
    """
    Get submission details.

    Args:
        submission_id: Submission ID
        session: Database session

    Returns:
        SubmissionWithDocuments with submission and document details
    """
    try:
        submission = submission_crud.get_submission(
            session=session, submission_id=submission_id
        )
        if not submission:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Submission not found: {submission_id}",
            )

        # Verify user owns the submission
        user_id = get_current_user_id()
        if submission.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied",
            )

        # Get submission documents
        documents = submission_crud.list_submission_documents(
            session=session, submission_id=submission_id
        )

        document_list = [
            SubmissionDocumentPublic(
                id=doc.id,
                submission_id=doc.submission_id,
                file_id=doc.file_id,
                document_type=doc.document_type,
                created_at=doc.created_at,
            )
            for doc in documents
        ]

        return SubmissionWithDocuments(
            id=submission.id,
            user_id=submission.user_id,
            task_id=submission.task_id,
            status=submission.status,
            created_at=submission.created_at,
            updated_at=submission.updated_at,
            documents=document_list,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting submission: {e}", exc_info=e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get submission: {str(e)}",
        )


@router.put(
    "/{submission_id}",
    response_model=SubmissionPublic,
    summary="Update submission",
    description="Update submission status.",
)
async def update_submission(
    submission_id: str,
    session: SessionDep,
    submission_in: SubmissionUpdate,
) -> SubmissionPublic:
    """
    Update a submission.

    Args:
        submission_id: Submission ID
        session: Database session
        submission_in: Submission update data

    Returns:
        SubmissionPublic with updated submission details
    """
    try:
        submission = submission_crud.get_submission(
            session=session, submission_id=submission_id
        )
        if not submission:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Submission not found: {submission_id}",
            )

        # Verify user owns the submission
        user_id = get_current_user_id()
        if submission.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied",
            )

        # Update submission
        updated_submission = submission_crud.update_submission(
            session=session,
            submission_id=submission_id,
            status=submission_in.status,
        )

        if not updated_submission:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update submission",
            )

        return SubmissionPublic(
            id=updated_submission.id,
            user_id=updated_submission.user_id,
            task_id=updated_submission.task_id,
            status=updated_submission.status,
            created_at=updated_submission.created_at,
            updated_at=updated_submission.updated_at,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating submission: {e}", exc_info=e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update submission: {str(e)}",
        )


@router.delete(
    "/{submission_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete submission",
    description="Delete a submission and its associated documents.",
)
async def delete_submission(
    submission_id: str,
    session: SessionDep,
) -> None:
    """
    Delete a submission.

    Args:
        submission_id: Submission ID
        session: Database session
    """
    try:
        submission = submission_crud.get_submission(
            session=session, submission_id=submission_id
        )
        if not submission:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Submission not found: {submission_id}",
            )

        # Verify user owns the submission
        user_id = get_current_user_id()
        if submission.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied",
            )

        # Delete submission (cascade deletes documents)
        submission_crud.delete_submission(session=session, submission_id=submission_id)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting submission: {e}", exc_info=e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete submission: {str(e)}",
        )
