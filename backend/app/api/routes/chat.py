"""Chat streaming API routes."""

import asyncio

from fastapi import APIRouter, Request, status
from fastapi.responses import StreamingResponse

from app.api.dependencies import CurrentUser, SessionDep
from app.core.config import settings
from app.core.constants import Tags
from app.core.logging import get_logger
from app.exceptions import AppException, ServiceUnavailableException
from app.schemas.chat import ChatRequest, ChatStreamEvent
from app.services.chat_service import chat_service

logger = get_logger(__name__)

router = APIRouter(prefix="/chat", tags=[Tags.CHAT])


def format_sse(event: ChatStreamEvent) -> str:
    """Serialize one SSE event payload."""
    return f"event: {event.event}\ndata: {event.model_dump_json()}\n\n"


@router.post(
    "",
    status_code=status.HTTP_200_OK,
    summary="Stream chat completion",
    description="Stream token-by-token assistant responses using SSE.",
)
async def stream_chat(
    payload: ChatRequest,
    request: Request,
    session: SessionDep,
    current_user: CurrentUser,
) -> StreamingResponse:
    """Stream LLM chat output as SSE while persisting conversation data."""
    if not settings.CHAT_STREAMING_ENABLED:
        raise ServiceUnavailableException(
            "Chat streaming is disabled",
            service="chat",
        )

    async def event_generator():
        try:
            async with chat_service.user_stream_guard(current_user.id):
                async for event in chat_service.stream_chat(
                    session=session,
                    user_id=current_user.id,
                    payload=payload,
                    disconnect_checker=request.is_disconnected,
                ):
                    yield format_sse(event)
        except asyncio.CancelledError:
            logger.info("Client disconnected from chat stream")
        except AppException as exc:
            yield format_sse(ChatStreamEvent(event="error", error=exc.message))
        except Exception as exc:
            logger.error("Unhandled chat stream error: %s", exc, exc_info=exc)
            yield format_sse(
                ChatStreamEvent(
                    event="error",
                    error="Internal server error",
                )
            )

    headers = {
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
        "X-Accel-Buffering": "no",
    }

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers=headers,
    )
