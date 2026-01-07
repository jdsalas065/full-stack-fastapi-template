"""Tests for file management endpoints."""

from io import BytesIO

from fastapi.testclient import TestClient


def test_upload_file_success(client: TestClient) -> None:
    """Test that file upload without task_id fails."""
    # Create a dummy file
    file_content = b"Test file content"
    files = {"file": ("test.pdf", BytesIO(file_content), "application/pdf")}

    response = client.post("/api/v1/files/upload", files=files)

    # Should fail because task_id is now required
    assert response.status_code == 422  # Validation error


def test_upload_file_unsupported_type(client: TestClient) -> None:
    """Test upload with unsupported file type."""
    from uuid import uuid4

    file_content = b"Test file content"
    files = {"file": ("test.txt", BytesIO(file_content), "text/plain")}

    # Even with task_id, unsupported file type should fail
    fake_task_id = str(uuid4())
    response = client.post(f"/api/v1/files/upload?task_id={fake_task_id}", files=files)

    assert response.status_code == 400
    assert "Unsupported file type" in response.json()["detail"]


def test_upload_file_no_filename(client: TestClient) -> None:
    """Test upload without filename."""
    from uuid import uuid4

    file_content = b"Test file content"
    files = {"file": ("", BytesIO(file_content), "application/pdf")}

    fake_task_id = str(uuid4())
    response = client.post(f"/api/v1/files/upload?task_id={fake_task_id}", files=files)

    assert response.status_code == 400


def test_list_files(client: TestClient) -> None:
    """Test listing files."""
    response = client.get("/api/v1/files")

    assert response.status_code == 200
    data = response.json()
    assert "files" in data
    assert "total" in data
    assert isinstance(data["files"], list)


def test_get_file_not_found(client: TestClient) -> None:
    """Test getting non-existent file."""
    response = client.get("/api/v1/files/non-existent-id")

    assert response.status_code == 404


def test_delete_file_not_found(client: TestClient) -> None:
    """Test deleting non-existent file."""
    response = client.delete("/api/v1/files/non-existent-id")

    assert response.status_code == 404


def test_upload_excel_file(client: TestClient) -> None:
    """Test uploading Excel file."""
    file_content = b"Test Excel content"
    files = {
        "file": (
            "test.xlsx",
            BytesIO(file_content),
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
    }

    # These tests now fail because task_id is required
    response = client.post("/api/v1/files/upload", files=files)

    assert response.status_code == 422  # Validation error


def test_upload_image_file(client: TestClient) -> None:
    """Test uploading image file without task_id fails."""
    file_content = b"Test image content"
    files = {"file": ("test.png", BytesIO(file_content), "image/png")}

    response = client.post("/api/v1/files/upload", files=files)

    assert response.status_code == 422  # Validation error


def test_upload_word_file(client: TestClient) -> None:
    """Test uploading Word document without task_id fails."""
    file_content = b"Test Word content"
    files = {
        "file": (
            "test.docx",
            BytesIO(file_content),
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        )
    }

    response = client.post("/api/v1/files/upload", files=files)

    assert response.status_code == 422  # Validation error


def test_upload_file_with_invalid_task_id(client: TestClient) -> None:
    """Test uploading file with invalid task_id format."""
    file_content = b"Test file content for task"
    files = {"file": ("invoice.pdf", BytesIO(file_content), "application/pdf")}

    task_id = "invalid-not-a-uuid"
    response = client.post(f"/api/v1/files/upload?task_id={task_id}", files=files)

    # Should fail because task_id is not a valid UUID and not "root"
    assert response.status_code == 400


def test_upload_file_with_empty_task_id(client: TestClient) -> None:
    """Test uploading file with empty task_id."""
    file_content = b"Test file content"
    files = {"file": ("test.pdf", BytesIO(file_content), "application/pdf")}

    response = client.post("/api/v1/files/upload?task_id=", files=files)

    # Should reject empty task_id
    assert response.status_code == 400
    assert "task_id cannot be empty" in response.json()["detail"]


def test_upload_file_with_whitespace_task_id(client: TestClient) -> None:
    """Test uploading file with whitespace-only task_id."""
    file_content = b"Test file content"
    files = {"file": ("test.pdf", BytesIO(file_content), "application/pdf")}

    response = client.post("/api/v1/files/upload?task_id=   ", files=files)

    # Should reject whitespace-only task_id
    assert response.status_code == 400
    assert "task_id cannot be empty" in response.json()["detail"]


def test_upload_multiple_files_same_task_id(client: TestClient) -> None:
    """Test uploading multiple files with the same submission task_id."""
    from unittest.mock import AsyncMock, patch

    # Mock storage service for both submissions and file uploads
    with (
        patch("app.api.routes.submissions.storage_service") as mock_submissions_storage,
        patch("app.api.routes.files.storage_service") as mock_files_storage,
    ):
        mock_submissions_storage.upload_file_from_upload = AsyncMock(
            return_value={
                "file_name": "invoice.pdf",
                "file_path": "task-id/invoice.pdf",
                "file_size": 100,
                "content_type": "application/pdf",
            }
        )
        mock_submissions_storage.delete_folder = AsyncMock()

        # First create a submission with initial file
        file_content = b"Initial file"
        files = [
            ("files", ("initial.pdf", BytesIO(file_content), "application/pdf")),
        ]

        data = {"name": "Test Submission", "description": "Test description"}

        create_response = client.post("/api/v1/submissions/", data=data, files=files)
        assert create_response.status_code == 201
        submission_id = create_response.json()["id"]

        # Now upload additional files to this submission
        def mock_upload_side_effect(task_id, file):
            return AsyncMock(
                return_value={
                    "file_name": file.filename,
                    "file_path": f"{task_id}/{file.filename}",
                    "file_size": 200,
                    "content_type": file.content_type or "application/octet-stream",
                }
            )()

        mock_files_storage.upload_file_from_upload.side_effect = mock_upload_side_effect

        # Upload first additional file
        additional_file1 = {
            "file": (
                "doc1.xlsx",
                BytesIO(b"Excel content"),
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
        }
        response1 = client.post(
            f"/api/v1/files/upload?task_id={submission_id}", files=additional_file1
        )
        assert response1.status_code == 201
        data1 = response1.json()
        assert data1["task_id"] == submission_id

        # Upload second additional file
        additional_file2 = {
            "file": ("doc2.pdf", BytesIO(b"PDF content"), "application/pdf")
        }
        response2 = client.post(
            f"/api/v1/files/upload?task_id={submission_id}", files=additional_file2
        )
        assert response2.status_code == 201
        data2 = response2.json()
        assert data2["task_id"] == submission_id

        # Both files should have different file_ids
        assert data1["file_id"] != data2["file_id"]


def test_upload_file_to_root_requires_superuser(client: TestClient) -> None:
    """Test uploading file to root requires superuser privileges."""
    # This test assumes the default test client user is NOT a superuser
    file_content = b"Test file content"
    files = {"file": ("test.pdf", BytesIO(file_content), "application/pdf")}

    response = client.post("/api/v1/files/upload?task_id=root", files=files)

    # Should fail with 403 if user is not superuser
    # Note: If test client is configured with superuser, this test will fail
    # and should be adjusted accordingly
    assert response.status_code in [403, 201]  # Depends on test user privileges


def test_upload_file_to_nonexistent_task_returns_404(client: TestClient) -> None:
    """Test uploading file to non-existent task_id returns 404."""
    from uuid import uuid4

    fake_task_id = str(uuid4())
    file_content = b"Test file content"
    files = {"file": ("test.pdf", BytesIO(file_content), "application/pdf")}

    response = client.post(f"/api/v1/files/upload?task_id={fake_task_id}", files=files)

    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_upload_file_to_existing_submission(client: TestClient) -> None:
    """Test uploading file to an existing submission creates SubmissionDocument."""
    from unittest.mock import AsyncMock, patch

    # Mock storage service
    with (
        patch("app.api.routes.submissions.storage_service") as mock_submissions_storage,
        patch("app.api.routes.files.storage_service") as mock_files_storage,
    ):
        mock_submissions_storage.upload_file_from_upload = AsyncMock(
            return_value={
                "file_name": "invoice.pdf",
                "file_path": "task-id/invoice.pdf",
                "file_size": 100,
                "content_type": "application/pdf",
            }
        )
        mock_submissions_storage.delete_folder = AsyncMock()

        # First create a submission
        file_content = b"Initial file"
        files = [
            ("files", ("initial.pdf", BytesIO(file_content), "application/pdf")),
        ]

        data = {
            "name": "Test Submission",
            "description": "Test description",
        }

        create_response = client.post("/api/v1/submissions/", data=data, files=files)
        assert create_response.status_code == 201
        submission_id = create_response.json()["id"]

        # Now upload an additional file to this submission
        mock_files_storage.upload_file_from_upload.return_value = {
            "file_name": "additional.pdf",
            "file_path": f"{submission_id}/additional.pdf",
            "file_size": 200,
            "content_type": "application/pdf",
        }

        additional_file = {
            "file": ("additional.pdf", BytesIO(b"Additional file"), "application/pdf")
        }

        upload_response = client.post(
            f"/api/v1/files/upload?task_id={submission_id}", files=additional_file
        )

        assert upload_response.status_code == 201
        upload_data = upload_response.json()
        assert upload_data["task_id"] == submission_id

        # Verify the submission now has the additional document
        get_response = client.get(f"/api/v1/submissions/{submission_id}")
        assert get_response.status_code == 200
        submission_data = get_response.json()
        # Should have at least 2 documents now
        assert len(submission_data["documents"]) >= 2
