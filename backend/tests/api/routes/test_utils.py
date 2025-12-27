from fastapi.testclient import TestClient


def test_health_check(client: TestClient) -> None:
    """Test health check endpoint."""
    response = client.get("/api/v1/utils/health-check/")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "OK"
