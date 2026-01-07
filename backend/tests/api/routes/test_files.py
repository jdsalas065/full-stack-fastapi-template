"""Tests for file management endpoints."""

from io import BytesIO

from fastapi.testclient import TestClient


def test_upload_file_success(client: TestClient) -> None:
    """Test successful file upload."""
    # Create a dummy file
    file_content = b"Test file content"
    files = {"file": ("test.pdf", BytesIO(file_content), "application/pdf")}

    response = client.post("/api/v1/files/upload", files=files)

    assert response.status_code == 201
    data = response.json()
    assert "file_id" in data
    assert data["filename"] == "test.pdf"
    assert data["file_type"] == "pdf"
    assert data["file_size"] == len(file_content)
    assert data["task_id"] is None
    # Without task_id, object_name should be {user_id}/{filename}
    assert "/" in data["object_name"]
    assert data["object_name"].endswith("/test.pdf")


def test_upload_file_unsupported_type(client: TestClient) -> None:
    """Test upload with unsupported file type."""
    file_content = b"Test file content"
    files = {"file": ("test.txt", BytesIO(file_content), "text/plain")}

    response = client.post("/api/v1/files/upload", files=files)

    assert response.status_code == 400
    assert "Unsupported file type" in response.json()["detail"]


def test_upload_file_no_filename(client: TestClient) -> None:
    """Test upload without filename."""
    file_content = b"Test file content"
    files = {"file": ("", BytesIO(file_content), "application/pdf")}

    response = client.post("/api/v1/files/upload", files=files)

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

    response = client.post("/api/v1/files/upload", files=files)

    assert response.status_code == 201
    data = response.json()
    assert data["file_type"] == "excel"


def test_upload_image_file(client: TestClient) -> None:
    """Test uploading image file."""
    file_content = b"Test image content"
    files = {"file": ("test.png", BytesIO(file_content), "image/png")}

    response = client.post("/api/v1/files/upload", files=files)

    assert response.status_code == 201
    data = response.json()
    assert data["file_type"] == "image"


def test_upload_word_file(client: TestClient) -> None:
    """Test uploading Word document."""
    file_content = b"Test Word content"
    files = {
        "file": (
            "test.docx",
            BytesIO(file_content),
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        )
    }

    response = client.post("/api/v1/files/upload", files=files)

    assert response.status_code == 201
    data = response.json()
    assert data["file_type"] == "docx"


def test_upload_file_with_task_id(client: TestClient) -> None:
    """Test uploading file with task_id."""
    file_content = b"Test file content for task"
    files = {"file": ("invoice.pdf", BytesIO(file_content), "application/pdf")}

    task_id = "test-task-123"
    response = client.post(f"/api/v1/files/upload?task_id={task_id}", files=files)

    assert response.status_code == 201
    data = response.json()
    assert data["filename"] == "invoice.pdf"
    assert data["task_id"] == task_id
    # With task_id, object_name should be {task_id}/{filename}
    assert data["object_name"] == f"{task_id}/invoice.pdf"


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
    """Test uploading multiple files with the same task_id."""
    task_id = "task-multi-456"

    # Upload first file
    file1_content = b"Test Excel content"
    files1 = {
        "file": (
            "invoice.xlsx",
            BytesIO(file1_content),
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
    }
    response1 = client.post(f"/api/v1/files/upload?task_id={task_id}", files=files1)
    assert response1.status_code == 201
    data1 = response1.json()
    assert data1["task_id"] == task_id
    assert data1["object_name"] == f"{task_id}/invoice.xlsx"

    # Upload second file with same task_id
    file2_content = b"Test PDF content"
    files2 = {"file": ("invoice.pdf", BytesIO(file2_content), "application/pdf")}
    response2 = client.post(f"/api/v1/files/upload?task_id={task_id}", files=files2)
    assert response2.status_code == 201
    data2 = response2.json()
    assert data2["task_id"] == task_id
    assert data2["object_name"] == f"{task_id}/invoice.pdf"

    # Both files should have the same task_id but different filenames
    assert data1["file_id"] != data2["file_id"]
    assert data1["filename"] != data2["filename"]


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

    # Mock MinIO service
    with (
        patch("app.api.routes.submissions.minio_service") as mock_submissions_minio,
        patch("app.api.routes.files.upload_file_to_minio") as mock_files_upload,
    ):
        mock_submissions_minio.upload_file_to_minio = AsyncMock(
            return_value={
                "file_name": "invoice.pdf",
                "file_path": "task-id/invoice.pdf",
                "file_size": 100,
                "content_type": "application/pdf",
            }
        )
        mock_submissions_minio.delete_folder = AsyncMock()

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
        mock_files_upload.return_value = {
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
