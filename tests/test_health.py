from fastapi.testclient import TestClient

from main import app


def test_health_endpoint_returns_healthy_status():
    client = TestClient(app)

    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
    assert response.json()["version"] == "0.2.0"


def test_health_endpoint_includes_middleware_headers():
    client = TestClient(app)

    response = client.get("/api/health")

    assert response.headers["X-Request-ID"]
    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert response.headers["X-Frame-Options"] == "DENY"
