"""Tests for submission management endpoints."""

from io import BytesIO
from unittest.mock import AsyncMock, patch
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def mock_storage_service():
    """Mock storage service to avoid actual file uploads during tests."""
    with patch("app.api.routes.submissions.storage_service") as mock:
        # Mock upload_file_from_upload to return predictable metadata
        mock.upload_file_from_upload = AsyncMock(
            return_value={
                "file_name": "test.pdf",
                "file_path": "task-id/test.pdf",
                "file_size": 100,
                "content_type": "application/pdf",
            }
        )
        # Mock delete_folder
        mock.delete_folder = AsyncMock()
        yield mock


def test_create_submission_happy_path(
    client: TestClient, mock_storage_service: AsyncMock
) -> None:
    """Test successful submission creation with files."""
    # Create test files
    file_content = b"Test PDF content"
    files = [
        ("files", ("invoice.pdf", BytesIO(file_content), "application/pdf")),
        ("files", ("receipt.pdf", BytesIO(file_content), "application/pdf")),
    ]

    data = {
        "name": "Test Submission",
        "description": "Test description",
        "pic": "test.jpg",
    }

    response = client.post("/api/v1/submissions/", data=data, files=files)

    assert response.status_code == 201
    json_data = response.json()

    # Verify response structure
    assert "id" in json_data
    assert json_data["name"] == "Test Submission"
    assert json_data["description"] == "Test description"
    assert json_data["pic"] == "test.jpg"
    assert "owner_id" in json_data
    assert "created_at" in json_data
    assert "documents" in json_data

    # Verify documents were created
    assert len(json_data["documents"]) == 2
    for doc in json_data["documents"]:
        assert "id" in doc
        assert "submission_id" in doc
        assert "file_name" in doc
        assert "file_path" in doc
        assert "file_size" in doc
        assert "uploaded_at" in doc


def test_create_submission_without_files(client: TestClient) -> None:
    """Test submission creation fails without files."""
    data = {
        "name": "Test Submission",
        "description": "Test description",
    }

    response = client.post("/api/v1/submissions/", data=data)

    # Should fail because files are required
    assert response.status_code == 422


def test_create_submission_without_name(client: TestClient) -> None:
    """Test submission creation fails without name."""
    file_content = b"Test PDF content"
    files = [
        ("files", ("invoice.pdf", BytesIO(file_content), "application/pdf")),
    ]

    data = {
        "description": "Test description",
    }

    response = client.post("/api/v1/submissions/", data=data, files=files)

    # Should fail because name is required
    assert response.status_code == 422


def test_get_submission_by_id(
    client: TestClient, mock_storage_service: AsyncMock
) -> None:
    """Test getting submission by ID."""
    # First create a submission
    file_content = b"Test PDF content"
    files = [
        ("files", ("invoice.pdf", BytesIO(file_content), "application/pdf")),
    ]

    data = {
        "name": "Test Submission",
        "description": "Test description",
    }

    create_response = client.post("/api/v1/submissions/", data=data, files=files)
    assert create_response.status_code == 201
    submission_id = create_response.json()["id"]

    # Now get the submission
    get_response = client.get(f"/api/v1/submissions/{submission_id}")

    assert get_response.status_code == 200
    json_data = get_response.json()
    assert json_data["id"] == submission_id
    assert json_data["name"] == "Test Submission"
    assert json_data["description"] == "Test description"
    assert len(json_data["documents"]) >= 1


def test_get_nonexistent_submission(client: TestClient) -> None:
    """Test getting non-existent submission returns 404."""
    fake_id = str(uuid4())
    response = client.get(f"/api/v1/submissions/{fake_id}")

    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_get_submission_access_denied(
    client: TestClient, mock_storage_service: AsyncMock
) -> None:
    """Test that non-owners cannot access submission (if multiple users exist)."""
    # This test assumes the test client uses a default user
    # For a proper test, we would need to:
    # 1. Create submission with user A
    # 2. Try to access with user B
    # 3. Verify 403 response
    #
    # Since the test setup uses a single user, we'll skip this for now
    # or implement when multi-user test fixtures are available
    pass


def test_create_submission_duplicate_name(
    client: TestClient, mock_storage_service: AsyncMock
) -> None:
    """Test that creating submission with duplicate name fails."""
    # Create first submission
    file_content = b"Test PDF content"
    files = [
        ("files", ("invoice.pdf", BytesIO(file_content), "application/pdf")),
    ]

    data = {
        "name": "Duplicate Test",
        "description": "First submission",
    }

    response = client.post("/api/v1/submissions/", data=data, files=files)
    assert response.status_code == 201

    # Try to create second submission with the same name
    files2 = [
        ("files", ("invoice2.pdf", BytesIO(file_content), "application/pdf")),
    ]

    data2 = {
        "name": "Duplicate Test",
        "description": "Second submission with same name",
    }

    response2 = client.post("/api/v1/submissions/", data=data2, files=files2)
    assert response2.status_code == 400
    assert "already exists" in response2.json()["detail"]
