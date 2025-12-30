"""Tests for file management endpoints."""

from io import BytesIO

from fastapi.testclient import TestClient


def test_upload_file_success(client: TestClient) -> None:
    """Test successful file upload."""
    # Create a dummy file
    file_content = b"Test file content"
    files = {
        "file": ("test.pdf", BytesIO(file_content), "application/pdf")
    }
    
    response = client.post("/api/v1/files/upload", files=files)
    
    assert response.status_code == 201
    data = response.json()
    assert "file_id" in data
    assert data["filename"] == "test.pdf"
    assert data["file_type"] == "pdf"
    assert data["file_size"] == len(file_content)


def test_upload_file_unsupported_type(client: TestClient) -> None:
    """Test upload with unsupported file type."""
    file_content = b"Test file content"
    files = {
        "file": ("test.txt", BytesIO(file_content), "text/plain")
    }
    
    response = client.post("/api/v1/files/upload", files=files)
    
    assert response.status_code == 400
    assert "Unsupported file type" in response.json()["detail"]


def test_upload_file_no_filename(client: TestClient) -> None:
    """Test upload without filename."""
    file_content = b"Test file content"
    files = {
        "file": ("", BytesIO(file_content), "application/pdf")
    }
    
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
        "file": ("test.xlsx", BytesIO(file_content), "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    }
    
    response = client.post("/api/v1/files/upload", files=files)
    
    assert response.status_code == 201
    data = response.json()
    assert data["file_type"] == "excel"


def test_upload_image_file(client: TestClient) -> None:
    """Test uploading image file."""
    file_content = b"Test image content"
    files = {
        "file": ("test.png", BytesIO(file_content), "image/png")
    }
    
    response = client.post("/api/v1/files/upload", files=files)
    
    assert response.status_code == 201
    data = response.json()
    assert data["file_type"] == "image"


def test_upload_word_file(client: TestClient) -> None:
    """Test uploading Word document."""
    file_content = b"Test Word content"
    files = {
        "file": ("test.docx", BytesIO(file_content), "application/vnd.openxmlformats-officedocument.wordprocessingml.document")
    }
    
    response = client.post("/api/v1/files/upload", files=files)
    
    assert response.status_code == 201
    data = response.json()
    assert data["file_type"] == "docx"
