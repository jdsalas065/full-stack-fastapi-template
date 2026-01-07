import uuid
from typing import Any

from fastapi import APIRouter, HTTPException
from sqlmodel import func, select

from app.api.deps import CurrentUser, SessionDep
from app.models import (
    Message,
    Submission,
    SubmissionCreate,
    SubmissionDocument,
    SubmissionPublic,
    SubmissionsPublic,
    SubmissionUpdate,
)
from app.services.minio import get_minio_service

router = APIRouter(prefix="/submissions", tags=["submissions"])


@router.get("/", response_model=SubmissionsPublic)
def read_submissions(
    session: SessionDep, current_user: CurrentUser, skip: int = 0, limit: int = 100
) -> Any:
    """
    Retrieve submissions.
    """
    if current_user.is_superuser:
        count_statement = select(func.count()).select_from(Submission)
        count = session.exec(count_statement).one()
        statement = select(Submission).offset(skip).limit(limit)
        submissions = session.exec(statement).all()
    else:
        count_statement = (
            select(func.count())
            .select_from(Submission)
            .where(Submission.owner_id == current_user.id)
        )
        count = session.exec(count_statement).one()
        statement = (
            select(Submission)
            .where(Submission.owner_id == current_user.id)
            .offset(skip)
            .limit(limit)
        )
        submissions = session.exec(statement).all()

    return SubmissionsPublic(data=submissions, count=count)


@router.get("/{id}", response_model=SubmissionPublic)
def read_submission(
    session: SessionDep, current_user: CurrentUser, id: uuid.UUID
) -> Any:
    """
    Get submission by ID.
    """
    submission = session.get(Submission, id)
    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")
    if not current_user.is_superuser and (submission.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    return submission


@router.post("/", response_model=SubmissionPublic)
def create_submission(
    *, session: SessionDep, current_user: CurrentUser, submission_in: SubmissionCreate
) -> Any:
    """
    Create new submission.
    """
    submission = Submission.model_validate(
        submission_in, update={"owner_id": current_user.id}
    )
    session.add(submission)
    session.commit()
    session.refresh(submission)
    return submission


@router.put("/{id}", response_model=SubmissionPublic)
def update_submission(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    id: uuid.UUID,
    submission_in: SubmissionUpdate,
) -> Any:
    """
    Update a submission.
    """
    submission = session.get(Submission, id)
    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")
    if not current_user.is_superuser and (submission.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    update_dict = submission_in.model_dump(exclude_unset=True)
    submission.sqlmodel_update(update_dict)
    session.add(submission)
    session.commit()
    session.refresh(submission)
    return submission


@router.delete("/{id}")
def delete_submission(
    session: SessionDep, current_user: CurrentUser, id: uuid.UUID
) -> Message:
    """
    Delete a submission.
    """
    submission = session.get(Submission, id)
    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")
    if not current_user.is_superuser and (submission.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")

    # Delete all associated documents from MinIO
    documents = session.exec(
        select(SubmissionDocument).where(SubmissionDocument.submission_id == id)
    ).all()
    minio_service = get_minio_service()
    for doc in documents:
        try:
            minio_service.delete_file(doc.file_path)
        except Exception:
            # Log the error but continue with deletion
            # In production, use proper logging
            pass

    # Delete submission (cascade will handle documents in DB)
    session.delete(submission)
    session.commit()
    return Message(message="Submission deleted successfully")
