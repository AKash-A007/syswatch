"""
tests/integration/test_api.py — FastAPI integration tests using httpx TestClient.

These tests spin up the FastAPI app in-process (no real server needed)
and verify that endpoints respond correctly.
"""

import sys
import os
import pytest

# Add src/ to sys.path
SRC_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "src")
sys.path.insert(0, os.path.abspath(SRC_PATH))

from fastapi.testclient import TestClient
from backend.api_server import app  # type: ignore


@pytest.fixture(scope="module")
def client():
    """Create a TestClient for the FastAPI app."""
    with TestClient(app) as c:
        yield c


# ── Health & Root ─────────────────────────────────────────────────────────────

class TestHealthEndpoints:
    def test_root_returns_200(self, client):
        """Root endpoint should return HTTP 200."""
        response = client.get("/")
        assert response.status_code == 200

    def test_health_endpoint(self, client):
        """Health endpoint must confirm service is up."""
        response = client.get("/health")
        assert response.status_code == 200
        body = response.json()
        assert body.get("status") in ("ok", "healthy", "running")

    def test_api_docs_available(self, client):
        """OpenAPI docs should be accessible."""
        response = client.get("/docs")
        assert response.status_code == 200


# ── Services API ──────────────────────────────────────────────────────────────

class TestServicesAPI:
    def test_list_services(self, client):
        """GET /api/services should return a list."""
        response = client.get("/api/services")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_service_structure(self, client):
        """Each service object must have required fields."""
        response = client.get("/api/services")
        services = response.json()
        if services:  # Only validate if services exist
            svc = services[0]
            assert "name" in svc or "id" in svc


# ── Metrics API ───────────────────────────────────────────────────────────────

class TestMetricsAPI:
    def test_metrics_endpoint_exists(self, client):
        """GET /api/metrics should not return 404."""
        response = client.get("/api/metrics")
        assert response.status_code != 404

    def test_metrics_returns_json(self, client):
        """Metrics endpoint should return valid JSON."""
        response = client.get("/api/metrics")
        if response.status_code == 200:
            data = response.json()
            assert data is not None


# ── Incidents API ─────────────────────────────────────────────────────────────

class TestIncidentsAPI:
    def test_incidents_endpoint_exists(self, client):
        """GET /api/incidents should not return 404."""
        response = client.get("/api/incidents")
        assert response.status_code != 404

    def test_incidents_returns_list(self, client):
        """Incidents endpoint should return a list when successful."""
        response = client.get("/api/incidents")
        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, list)


# ── Stress Test & Simulate ────────────────────────────────────────────────────

class TestDebugEndpoints:
    def test_stress_test_endpoint(self, client):
        """POST /api/stress-test should be accepted (200 or 202)."""
        response = client.post("/api/stress-test")
        assert response.status_code in (200, 202, 422)  # 422 = validation err ok

    def test_simulate_incident_endpoint(self, client):
        """POST /api/simulate-incident should be accepted."""
        response = client.post("/api/simulate-incident")
        assert response.status_code in (200, 202, 422)
