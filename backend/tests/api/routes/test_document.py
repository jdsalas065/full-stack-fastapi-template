"""Tests for document processing endpoints."""

from fastapi.testclient import TestClient


def test_process_document_submission_success(client: TestClient) -> None:
    """Test successful document submission processing."""
    payload = {"task_id": "test-task-123"}
    
    response = client.post(
        "/api/v1/document/process_document_submission",
        json=payload
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "processed"
    assert "result" in data
    assert data["result"]["task_id"] == "test-task-123"


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
    
    # Should accept empty string as valid (no min_length constraint)
    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "processed"
