from fastapi import APIRouter

from app.core.constants import Tags
from app.schemas import Message

router = APIRouter(prefix="/utils", tags=[Tags.UTILS])


@router.get("/health-check/")
async def health_check() -> Message:
    """
    Health check endpoint.

    Returns a simple OK message to verify the API is running.
    """
    return Message(message="OK")
