"""
Tests de integración para la ruta GET /health.
"""


class TestHealthRoute:
    def test_health_returns_200(self, client):
        """GET /health → status HTTP 200."""
        response = client.get("/health")
        assert response.status_code == 200

    def test_health_response_structure(self, client):
        """La respuesta tiene las claves status, provider, model, env."""
        response = client.get("/health")
        data = response.json()
        assert "status" in data
        assert "provider" in data
        assert "model" in data
        assert "env" in data

    def test_health_status_ok(self, client):
        """response['status'] == 'ok'."""
        response = client.get("/health")
        assert response.json()["status"] == "ok"

    def test_health_provider_matches_settings(self, client):
        """response['provider'] coincide con la variable LLM_PROVIDER del entorno."""
        from app.core.config import get_settings

        response = client.get("/health")
        settings = get_settings()
        assert response.json()["provider"] == settings.LLM_PROVIDER
