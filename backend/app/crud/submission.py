"""
Submission CRUD operations.

Database-backed CRUD operations for submission and submission documents.
"""

from datetime import datetime, timezone

from sqlmodel import Session, select

from app.core.logging import get_logger
from app.models.submission import Submission, SubmissionDocument

logger = get_logger(__name__)


def create_submission(
    *,
    session: Session,
    user_id: str,
    task_id: str,
    status: str = "pending",
) -> Submission:
    """
    Create a new submission record.

    Args:
        session: Database session
        user_id: ID of the user creating the submission
        task_id: Unique task identifier
        status: Submission status (default: "pending")

    Returns:
        Submission instance
    """
    db_obj = Submission(
        user_id=user_id,
        task_id=task_id,
        status=status,
    )
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    logger.info(f"Created submission record: {db_obj.id} for task: {task_id}")
    return db_obj


def get_submission(*, session: Session, submission_id: str) -> Submission | None:
    """
    Get submission by ID.

    Args:
        session: Database session
        submission_id: Submission ID

    Returns:
        Submission instance if found, None otherwise
    """
    return session.get(Submission, submission_id)


def get_submission_by_task_id(*, session: Session, task_id: str) -> Submission | None:
    """
    Get submission by task_id.

    Args:
        session: Database session
        task_id: Task ID

    Returns:
        Submission instance if found, None otherwise
    """
    statement = select(Submission).where(Submission.task_id == task_id)
    return session.exec(statement).first()


def list_submissions_by_user(*, session: Session, user_id: str) -> list[Submission]:
    """
    List all submissions for a user.

    Args:
        session: Database session
        user_id: User ID

    Returns:
        List of Submission instances
    """
    statement = select(Submission).where(Submission.user_id == user_id)
    return list(session.exec(statement).all())


def update_submission(
    *, session: Session, submission_id: str, status: str | None = None
) -> Submission | None:
    """
    Update submission.

    Args:
        session: Database session
        submission_id: Submission ID
        status: New status

    Returns:
        Updated Submission instance or None if not found
    """
    submission = session.get(Submission, submission_id)
    if not submission:
        return None

    if status is not None:
        submission.status = status

    submission.updated_at = datetime.now(timezone.utc)
    session.add(submission)
    session.commit()
    session.refresh(submission)
    logger.info(f"Updated submission: {submission_id}")
    return submission


def delete_submission(*, session: Session, submission_id: str) -> bool:
    """
    Delete submission and its documents.

    Args:
        session: Database session
        submission_id: Submission ID

    Returns:
        True if deleted, False if not found
    """
    submission = session.get(Submission, submission_id)
    if submission:
        session.delete(submission)
        session.commit()
        logger.info(f"Deleted submission: {submission_id}")
        return True
    return False


# SubmissionDocument CRUD operations
def create_submission_document(
    *,
    session: Session,
    submission_id: str,
    file_id: str,
    document_type: str | None = None,
) -> SubmissionDocument:
    """
    Create a submission document link.

    Args:
        session: Database session
        submission_id: Submission ID
        file_id: File ID
        document_type: Optional document type

    Returns:
        SubmissionDocument instance
    """
    db_obj = SubmissionDocument(
        submission_id=submission_id,
        file_id=file_id,
        document_type=document_type,
    )
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    logger.info(
        f"Created submission document: {db_obj.id} (submission: {submission_id}, file: {file_id})"
    )
    return db_obj


def list_submission_documents(
    *, session: Session, submission_id: str
) -> list[SubmissionDocument]:
    """
    List all documents for a submission.

    Args:
        session: Database session
        submission_id: Submission ID

    Returns:
        List of SubmissionDocument instances
    """
    statement = select(SubmissionDocument).where(
        SubmissionDocument.submission_id == submission_id
    )
    return list(session.exec(statement).all())


def delete_submission_document(
    *, session: Session, submission_document_id: str
) -> bool:
    """
    Delete a submission document link.

    Args:
        session: Database session
        submission_document_id: SubmissionDocument ID

    Returns:
        True if deleted, False if not found
    """
    doc = session.get(SubmissionDocument, submission_document_id)
    if doc:
        session.delete(doc)
        session.commit()
        logger.info(f"Deleted submission document: {submission_document_id}")
        return True
    return False
