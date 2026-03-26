"""
Tests de integración para verificar que el endpoint legacy POST /api/analyze fue eliminado.

El nuevo endpoint es POST /api/v1/patients/{patient_id}/analyze.
Ver test_analyze_v1.py para los tests del endpoint actual.
"""

from fastapi.testclient import TestClient


class TestLegacyEndpointRemoved:
    def test_legacy_analyze_endpoint_does_not_exist(self, client: TestClient):
        """
        POST /api/analyze ya no existe — debe retornar 404 o 405.
        El endpoint fue reemplazado por POST /api/v1/patients/{id}/analyze.
        """
        response = client.post(
            "/api/analyze",
            json={"historia_clinica": "Historia clínica de prueba con más de diez caracteres."},
        )
        assert response.status_code in (404, 405)

    def test_legacy_analyze_with_prefix_does_not_exist(self, client: TestClient):
        """
        POST /api/v1/analyze tampoco existe como ruta de top-level.
        """
        response = client.post(
            "/api/v1/analyze",
            json={"historia_clinica": "Historia clínica de prueba con más de diez caracteres."},
        )
        assert response.status_code in (404, 405)
