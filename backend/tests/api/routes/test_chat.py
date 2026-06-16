"""Tests for chat streaming endpoint."""

from collections.abc import AsyncIterator, Generator
from contextlib import asynccontextmanager
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from app.api.dependencies import get_current_active_user
from app.main import app
from app.models.user import User
from app.schemas.chat import ChatStreamEvent


@asynccontextmanager
async def allow_streams(_user_id: str) -> AsyncIterator[None]:
    """Mock user stream guard context manager."""
    yield


async def mock_stream_chat(**_kwargs):
    """Mock chat streaming service output."""
    yield ChatStreamEvent(event="start")
    yield ChatStreamEvent(event="token", delta="Xin ")
    yield ChatStreamEvent(event="token", delta="chao")
    yield ChatStreamEvent(event="done", content="Xin chao")


@pytest.fixture
def override_current_user() -> Generator[None, None, None]:
    """Override auth dependency for route tests that should bypass DB login."""

    def _mock_current_user() -> User:
        return User(
            id="test-user-id",
            email="test@example.com",
            hashed_password="not-used",
            is_active=True,
            is_superuser=True,
        )

    app.dependency_overrides[get_current_active_user] = _mock_current_user
    yield
    app.dependency_overrides.pop(get_current_active_user, None)


def test_chat_requires_auth(client: TestClient) -> None:
    """Endpoint should reject unauthenticated requests."""
    response = client.post("/api/v1/chat", json={"message": "hello"})

    assert response.status_code == 401


def test_chat_stream_success(client: TestClient, override_current_user: None) -> None:
    """Endpoint should stream SSE events for authenticated users."""
    with (
        patch("app.api.routes.chat.chat_service.user_stream_guard", new=allow_streams),
        patch("app.api.routes.chat.chat_service.stream_chat", new=mock_stream_chat),
    ):
        with client.stream(
            "POST",
            "/api/v1/chat",
            json={"message": "Xin chao"},
        ) as response:
            assert response.status_code == 200
            assert response.headers["content-type"].startswith("text/event-stream")
            body = "\n".join(response.iter_lines())

    assert "event: start" in body
    assert "event: token" in body
    assert "Xin " in body
    assert "event: done" in body
    assert "Xin chao" in body


def test_chat_disabled_returns_503(client: TestClient, override_current_user: None) -> None:
    """Endpoint should return 503 when chat streaming feature is disabled."""
    with patch("app.api.routes.chat.settings.CHAT_STREAMING_ENABLED", False):
        response = client.post(
            "/api/v1/chat",
            json={"message": "hello"},
        )

    assert response.status_code == 503
