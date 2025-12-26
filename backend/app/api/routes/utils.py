from fastapi import APIRouter

from app.schemas import Message

router = APIRouter(prefix="/utils", tags=["utils"])


@router.get("/health-check/")
async def health_check() -> Message:
    """
    Health check endpoint.
    """
    return Message(message="OK")
