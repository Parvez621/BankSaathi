
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_check():
    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert "database_url" not in response.json()


def test_verified_workflows_only():
    response = client.get("/api/workflows")

    assert response.status_code == 200
    data = response.json()

    assert data["total"] == 0
    assert data["workflows"] == []


def test_simulation_catalog():
    response = client.get(
        "/api/workflows?include_simulations=true"
    )

    assert response.status_code == 200
    data = response.json()

    assert data["total"] == 3

    for workflow in data["workflows"]:
        assert workflow["verification_status"] == "simulation"


def test_untrusted_host_rejected():
    response = client.get(
        "/api/health",
        headers={"Host": "malicious.example"},
    )

    assert response.status_code == 400


def test_security_headers():
    response = client.get("/api/health")

    assert response.headers["x-content-type-options"] == "nosniff"
    assert response.headers["cache-control"] == "no-store"
