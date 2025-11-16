import pytest


class TestHealthAPI:
    """Test health check endpoint."""

    def test_health_check(self, client):
        """Test health check endpoint returns healthy status."""
        response = client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data

    def test_health_check_version(self, client):
        """Test health check returns correct version."""
        response = client.get("/api/health")
        assert response.json()["version"] == "1.0.0"
