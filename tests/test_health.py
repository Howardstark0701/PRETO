from fastapi.testclient import TestClient

from app.api.auth import check_user_rate_limit, user_rate_limiter
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


def test_metrics_endpoint_exposes_prometheus_text():
    client = TestClient(app)

    client.get("/api/health")
    response = client.get("/api/metrics")

    assert response.status_code == 200
    assert "text/plain" in response.headers["content-type"]
    assert "preto_requests_total" in response.text
    assert 'route="/api/health"' in response.text


def test_dashboard_endpoint_returns_product_surface():
    client = TestClient(app)

    response = client.get("/dashboard")

    assert response.status_code == 200
    assert "PRETO Dashboard" in response.text
    assert "Search Repositories" in response.text


def test_user_rate_limiter_rejects_after_limit():
    user_id = 999_001
    user_rate_limiter.reset(user_id)

    first = check_user_rate_limit(user_id, rate_limit=1)
    second = check_user_rate_limit(user_id, rate_limit=1)

    assert first["allowed"] is True
    assert first["remaining"] == 0
    assert second["allowed"] is False
    assert second["limit"] == 1
