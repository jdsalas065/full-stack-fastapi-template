import uuid

from fastapi.testclient import TestClient
from sqlmodel import Session

from app.core.config import settings


def test_create_submission(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    data = {"title": "Test Submission", "description": "Test description"}
    response = client.post(
        f"{settings.API_V1_STR}/submissions/",
        headers=superuser_token_headers,
        json=data,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["title"] == data["title"]
    assert content["description"] == data["description"]
    assert "id" in content
    assert "owner_id" in content


def test_read_submission(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    # Create a submission first
    data = {"title": "Test Submission", "description": "Test description"}
    create_response = client.post(
        f"{settings.API_V1_STR}/submissions/",
        headers=superuser_token_headers,
        json=data,
    )
    submission_id = create_response.json()["id"]

    # Read the submission
    response = client.get(
        f"{settings.API_V1_STR}/submissions/{submission_id}",
        headers=superuser_token_headers,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["title"] == data["title"]
    assert content["description"] == data["description"]


def test_read_submission_not_found(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    response = client.get(
        f"{settings.API_V1_STR}/submissions/{uuid.uuid4()}",
        headers=superuser_token_headers,
    )
    assert response.status_code == 404
    content = response.json()
    assert content["detail"] == "Submission not found"


def test_read_submissions(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    response = client.get(
        f"{settings.API_V1_STR}/submissions/",
        headers=superuser_token_headers,
    )
    assert response.status_code == 200
    content = response.json()
    assert "data" in content
    assert "count" in content


def test_update_submission(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    # Create a submission first
    data = {"title": "Original Title", "description": "Original description"}
    create_response = client.post(
        f"{settings.API_V1_STR}/submissions/",
        headers=superuser_token_headers,
        json=data,
    )
    submission_id = create_response.json()["id"]

    # Update the submission
    update_data = {"title": "Updated Title", "description": "Updated description"}
    response = client.put(
        f"{settings.API_V1_STR}/submissions/{submission_id}",
        headers=superuser_token_headers,
        json=update_data,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["title"] == update_data["title"]
    assert content["description"] == update_data["description"]


def test_delete_submission(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    # Create a submission first
    data = {"title": "To Delete", "description": "Will be deleted"}
    create_response = client.post(
        f"{settings.API_V1_STR}/submissions/",
        headers=superuser_token_headers,
        json=data,
    )
    submission_id = create_response.json()["id"]

    # Delete the submission
    response = client.delete(
        f"{settings.API_V1_STR}/submissions/{submission_id}",
        headers=superuser_token_headers,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["message"] == "Submission deleted successfully"

    # Verify it's deleted
    get_response = client.get(
        f"{settings.API_V1_STR}/submissions/{submission_id}",
        headers=superuser_token_headers,
    )
    assert get_response.status_code == 404
