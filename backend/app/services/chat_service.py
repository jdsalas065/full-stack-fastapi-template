"""Chat streaming service with persistence and guardrails."""

import asyncio
from collections.abc import AsyncIterator, Awaitable, Callable
from contextlib import asynccontextmanager
from uuid import UUID

from openai import APIError, AsyncOpenAI, RateLimitError
from sqlmodel import Session, select

from app.core.config import settings
from app.core.logging import get_logger
from app.exceptions import NotFoundException, RateLimitException, ServiceUnavailableException
from app.models.chat import ChatConversation, ChatMessage
from app.schemas.chat import ChatRequest, ChatStreamEvent

logger = get_logger(__name__)

DEFAULT_SYSTEM_PROMPT = (
    "You are a helpful assistant. Keep answers concise, correct, and actionable."
)


class ChatService:
    """Service orchestrating conversation persistence and LLM streaming."""

    def __init__(self) -> None:
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY or "")
        self.default_model = settings.OPENAI_MODEL
        self._user_stream_counts: dict[str, int] = {}
        self._count_lock = asyncio.Lock()

    @asynccontextmanager
    async def user_stream_guard(self, user_id: str) -> AsyncIterator[None]:
        """Enforce per-user in-flight chat stream limit."""
        limit = max(1, settings.CHAT_MAX_CONCURRENT_PER_USER)

        async with self._count_lock:
            current = self._user_stream_counts.get(user_id, 0)
            if current >= limit:
                raise RateLimitException(
                    message="Too many concurrent chat streams for this user",
                )
            self._user_stream_counts[user_id] = current + 1

        try:
            yield
        finally:
            async with self._count_lock:
                current = self._user_stream_counts.get(user_id, 1)
                if current <= 1:
                    self._user_stream_counts.pop(user_id, None)
                else:
                    self._user_stream_counts[user_id] = current - 1

    def _get_or_create_conversation(
        self,
        *,
        session: Session,
        user_id: str,
        payload: ChatRequest,
    ) -> ChatConversation:
        if payload.conversation_id is not None:
            conversation = session.get(ChatConversation, payload.conversation_id)
            if conversation is None or conversation.owner_id != user_id:
                raise NotFoundException(
                    "Conversation not found",
                    resource=str(payload.conversation_id),
                )
            return conversation

        conversation = ChatConversation(
            owner_id=user_id,
            title=payload.message[:80],
        )
        session.add(conversation)
        session.commit()
        session.refresh(conversation)
        return conversation

    def _build_openai_messages(
        self,
        *,
        session: Session,
        conversation_id: UUID,
        user_message: str,
    ) -> list[dict[str, str]]:
        statement = (
            select(ChatMessage)
            .where(ChatMessage.conversation_id == conversation_id)
            .order_by(ChatMessage.created_at)
            .limit(settings.CHAT_HISTORY_LIMIT)
        )
        previous_messages = list(session.exec(statement))

        messages: list[dict[str, str]] = [
            {
                "role": "system",
                "content": DEFAULT_SYSTEM_PROMPT,
            }
        ]

        for message in previous_messages:
            if message.role not in {"user", "assistant", "system"}:
                continue
            messages.append(
                {
                    "role": message.role,
                    "content": message.content,
                }
            )

        messages.append(
            {
                "role": "user",
                "content": user_message,
            }
        )
        return messages

    async def _create_stream_with_retry(
        self,
        *,
        messages: list[dict[str, str]],
        payload: ChatRequest,
    ):
        retries = settings.CHAT_MAX_RETRIES if settings.CHAT_RETRY_ENABLED else 0
        delay = settings.CHAT_RETRY_INITIAL_DELAY_SECONDS

        for attempt in range(retries + 1):
            try:
                request_data = {
                    "model": payload.model or self.default_model,
                    "messages": messages,
                    "temperature": payload.temperature,
                    "stream": True,
                }
                if payload.max_tokens is not None:
                    request_data["max_tokens"] = payload.max_tokens

                return await self.client.chat.completions.create(**request_data)
            except (RateLimitError, APIError):
                if attempt >= retries:
                    raise
                await asyncio.sleep(delay)
                delay = min(delay * 2, 5.0)

        raise RuntimeError("Failed to create stream after retries")

    def _persist_assistant_message(
        self,
        *,
        session: Session,
        conversation_id: UUID,
        content: str,
        status: str,
        token_count: int,
    ) -> ChatMessage:
        assistant_message = ChatMessage(
            conversation_id=conversation_id,
            role="assistant",
            content=content,
            status=status,
            token_count=token_count,
        )
        session.add(assistant_message)
        session.commit()
        session.refresh(assistant_message)
        return assistant_message

    async def stream_chat(
        self,
        *,
        session: Session,
        user_id: str,
        payload: ChatRequest,
        disconnect_checker: Callable[[], Awaitable[bool]] | None = None,
    ) -> AsyncIterator[ChatStreamEvent]:
        """Stream assistant tokens while persisting conversation state."""
        if not settings.OPENAI_API_KEY:
            raise ServiceUnavailableException(
                "OpenAI API key not configured",
                service="openai",
            )

        conversation = self._get_or_create_conversation(
            session=session,
            user_id=user_id,
            payload=payload,
        )

        user_message = ChatMessage(
            conversation_id=conversation.id,
            role="user",
            content=payload.message,
            status="completed",
        )
        session.add(user_message)
        session.commit()
        session.refresh(user_message)

        yield ChatStreamEvent(
            event="start",
            conversation_id=conversation.id,
            message_id=user_message.id,
        )

        messages = self._build_openai_messages(
            session=session,
            conversation_id=conversation.id,
            user_message=payload.message,
        )

        chunks: list[str] = []
        token_count = 0

        try:
            stream = await asyncio.wait_for(
                self._create_stream_with_retry(messages=messages, payload=payload),
                timeout=settings.CHAT_STREAM_TIMEOUT_SECONDS,
            )

            loop = asyncio.get_running_loop()
            started_at = loop.time()
            last_heartbeat_at = started_at

            async for chunk in stream:
                if disconnect_checker is not None and await disconnect_checker():
                    raise asyncio.CancelledError("Client disconnected")

                now = loop.time()
                if now - started_at > settings.CHAT_STREAM_TIMEOUT_SECONDS:
                    raise asyncio.TimeoutError("Chat stream exceeded timeout")

                delta = ""
                if chunk.choices:
                    delta = chunk.choices[0].delta.content or ""

                if delta:
                    chunks.append(delta)
                    token_count += 1
                    yield ChatStreamEvent(
                        event="token",
                        conversation_id=conversation.id,
                        delta=delta,
                    )
                    last_heartbeat_at = now
                elif (
                    settings.CHAT_HEARTBEAT_ENABLED
                    and now - last_heartbeat_at
                    >= settings.CHAT_HEARTBEAT_INTERVAL_SECONDS
                ):
                    yield ChatStreamEvent(
                        event="heartbeat",
                        conversation_id=conversation.id,
                    )
                    last_heartbeat_at = now

            final_content = "".join(chunks).strip()
            assistant_message = self._persist_assistant_message(
                session=session,
                conversation_id=conversation.id,
                content=final_content,
                status="completed",
                token_count=token_count,
            )

            yield ChatStreamEvent(
                event="done",
                conversation_id=conversation.id,
                message_id=assistant_message.id,
                content=final_content,
            )
        except asyncio.CancelledError as exc:
            partial_content = "".join(chunks).strip()
            if partial_content:
                self._persist_assistant_message(
                    session=session,
                    conversation_id=conversation.id,
                    content=partial_content,
                    status="cancelled",
                    token_count=token_count,
                )
            logger.info("Chat stream cancelled for conversation %s", conversation.id)
            raise exc
        except asyncio.TimeoutError as exc:
            partial_content = "".join(chunks).strip()
            if partial_content:
                self._persist_assistant_message(
                    session=session,
                    conversation_id=conversation.id,
                    content=partial_content,
                    status="failed",
                    token_count=token_count,
                )
            raise ServiceUnavailableException(
                "Chat request timed out",
                service="openai",
            ) from exc
        except (RateLimitError, APIError) as exc:
            partial_content = "".join(chunks).strip()
            if partial_content:
                self._persist_assistant_message(
                    session=session,
                    conversation_id=conversation.id,
                    content=partial_content,
                    status="failed",
                    token_count=token_count,
                )
            raise ServiceUnavailableException(
                "OpenAI API error while streaming chat",
                service="openai",
            ) from exc
        except Exception as exc:
            partial_content = "".join(chunks).strip()
            if partial_content:
                self._persist_assistant_message(
                    session=session,
                    conversation_id=conversation.id,
                    content=partial_content,
                    status="failed",
                    token_count=token_count,
                )
            raise ServiceUnavailableException(
                f"Chat streaming failed: {str(exc)}",
                service="openai",
            ) from exc


chat_service = ChatService()
