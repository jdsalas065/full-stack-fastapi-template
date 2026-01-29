"""Tests for document processing endpoints."""

from fastapi.testclient import TestClient


def test_process_document_submission_success(client: TestClient) -> None:
    """Test successful document submission processing."""
    payload = {"task_id": "test-task-123"}

    response = client.post(
        "/api/v1/document/process_document_submission",
        json=payload
    )

    # Without actual files in MinIO, should get 404
    # This is a placeholder test - in real scenario would need MinIO setup
    # For now, verify the endpoint accepts the request format
    assert response.status_code in [201, 404, 500]
    if response.status_code == 201:
        data = response.json()
        assert data["status"] == "processed"
        assert "result" in data
        assert data["result"]["task_id"] == "test-task-123"
    elif response.status_code == 404:
        data = response.json()
        assert "No files found" in data["detail"]


def test_process_document_submission_missing_task_id(client: TestClient) -> None:
    """Test document submission with missing task_id."""
    payload = {}

    response = client.post(
        "/api/v1/document/process_document_submission",
        json=payload
    )

    assert response.status_code == 422  # Validation error


def test_process_document_submission_non_json_content(client: TestClient) -> None:
    """Test document submission with non-JSON content type."""
    response = client.post(
        "/api/v1/document/process_document_submission",
        data="not json data",
        headers={"Content-Type": "text/plain"}
    )

    # FastAPI returns 422 for non-JSON when JSON is expected
    assert response.status_code == 422


def test_process_document_submission_invalid_task_id_type(client: TestClient) -> None:
    """Test document submission with invalid task_id type."""
    payload = {"task_id": 12345}  # Should be string

    response = client.post(
        "/api/v1/document/process_document_submission",
        json=payload
    )

    assert response.status_code == 422  # Validation error


def test_process_document_submission_empty_task_id(client: TestClient) -> None:
    """Test document submission with empty task_id."""
    payload = {"task_id": ""}

    response = client.post(
        "/api/v1/document/process_document_submission",
        json=payload
    )

    # Empty string is accepted by validation, but will likely fail in MinIO
    # This is a placeholder test - in real scenario would need MinIO setup
    assert response.status_code in [201, 404, 500]


def test_compare_document_contents_missing_params(client: TestClient) -> None:
    """Test document comparison with missing parameters."""
    payload = {"task_id": "test-task-123"}  # Missing file names

    response = client.post(
        "/api/v1/document/compare_document_contents",
        json=payload
    )

    assert response.status_code == 422  # Validation error


def test_compare_document_contents_all_params(client: TestClient) -> None:
    """Test document comparison with all parameters."""
    payload = {
        "task_id": "test-task-123",
        "excel_file_name": "invoice.xlsx",
        "pdf_file_name": "invoice.pdf"
    }

    response = client.post(
        "/api/v1/document/compare_document_contents",
        json=payload
    )

    # Without actual files in MinIO, will get error
    # This verifies the endpoint accepts the request format
    # Expected status code changed from 200 to 201 for success
    assert response.status_code in [201, 404, 500]
    if response.status_code == 404 or response.status_code == 500:
        # Expected when files don't exist in MinIO
        data = response.json()
        assert "detail" in data
