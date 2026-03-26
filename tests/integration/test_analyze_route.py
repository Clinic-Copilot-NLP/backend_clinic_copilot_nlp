"""
Tests de integración para la ruta POST /api/analyze.
"""

import pytest
from fastapi.testclient import TestClient

from app.infrastructure.llm.base import LLMProvider, LLMProviderError, LLMResponse


# ---------------------------------------------------------------------------
# Proveedores fake para inyección de errores en tests específicos
# ---------------------------------------------------------------------------


class _LLMErrorProvider(LLMProvider):
    """Proveedor que lanza LLMProviderError siempre."""

    @property
    def provider_name(self) -> str:
        return "error-provider"

    async def generate(self, system_prompt: str, user_prompt: str) -> LLMResponse:
        raise LLMProviderError("Fallo simulado del LLM", self.provider_name)


class _NotImplementedProvider(LLMProvider):
    """Proveedor que lanza NotImplementedError siempre."""

    @property
    def provider_name(self) -> str:
        return "stub-provider"

    async def generate(self, system_prompt: str, user_prompt: str) -> LLMResponse:
        raise NotImplementedError("Proveedor no implementado.")


# ---------------------------------------------------------------------------
# Tests usando el fixture `client` (FakeLLMProvider inyectado)
# ---------------------------------------------------------------------------


class TestAnalyzeHappyPath:
    def test_analyze_happy_path(self, client, valid_historia):
        """Historia válida (100+ chars) → 200, con campos de metadata."""
        response = client.post("/api/analyze", json={"historia_clinica": valid_historia})
        assert response.status_code == 200
        data = response.json()
        assert "proveedor" in data
        assert "modelo" in data
        assert "tiempo_procesamiento_ms" in data

    def test_analyze_response_schema(self, client, valid_historia):
        """La respuesta incluye todos los campos de AnalyzeResponse."""
        response = client.post("/api/analyze", json={"historia_clinica": valid_historia})
        assert response.status_code == 200
        data = response.json()
        # Campos obligatorios del schema
        assert "proveedor" in data
        assert "modelo" in data
        assert "tiempo_procesamiento_ms" in data
        # Campos opcionales (presentes o None)
        assert "resumen_ejecutivo" in data
        assert "tokens_entrada" in data
        assert "tokens_salida" in data


class TestAnalyzeValidation:
    def test_analyze_invalid_too_short(self, client):
        """Historia demasiado corta → 422."""
        response = client.post("/api/analyze", json={"historia_clinica": "corto"})
        assert response.status_code == 422

    def test_analyze_invalid_too_long(self, client):
        """Historia con 50.001 chars → 422."""
        response = client.post("/api/analyze", json={"historia_clinica": "x" * 50_001})
        assert response.status_code == 422

    def test_analyze_missing_field(self, client):
        """Body vacío → 422."""
        response = client.post("/api/analyze", json={})
        assert response.status_code == 422

    def test_analyze_whitespace_only(self, client):
        """Solo espacios en blanco → strip → demasiado corto → 422."""
        response = client.post("/api/analyze", json={"historia_clinica": "   "})
        assert response.status_code == 422


class TestAnalyzeErrorHandling:
    def _client_with_provider(self, provider: LLMProvider) -> TestClient:
        """
        Crea un TestClient con el proveedor indicado inyectado en app.state.
        Devuelve el cliente como context manager para que se use con `with`.
        El proveedor se inyecta DESPUÉS de que el lifespan corre, sobrescribiéndolo.
        """
        from app.main import app

        # Usamos un wrapper para inyectar el proveedor dentro del bloque with
        class _ManagedClient:
            def __enter__(self_inner):
                self_inner._tc = TestClient(app, raise_server_exceptions=False)
                self_inner._tc.__enter__()
                # Lifespan ya corrió — sobreescribimos el proveedor
                app.state.llm_provider = provider
                return self_inner._tc

            def __exit__(self_inner, *args):
                return self_inner._tc.__exit__(*args)

        return _ManagedClient()  # type: ignore[return-value]

    def test_analyze_llm_provider_error(self, valid_historia):
        """LLMProviderError del proveedor → HTTP 503."""
        with self._client_with_provider(_LLMErrorProvider()) as test_client:
            response = test_client.post("/api/analyze", json={"historia_clinica": valid_historia})
        assert response.status_code == 503

    def test_analyze_not_implemented_error(self, valid_historia):
        """NotImplementedError del proveedor → HTTP 501."""
        with self._client_with_provider(_NotImplementedProvider()) as test_client:
            response = test_client.post("/api/analyze", json={"historia_clinica": valid_historia})
        assert response.status_code == 501

    def test_analyze_503_response_has_detail(self, valid_historia):
        """Respuesta 503 incluye clave 'detail' en el body."""
        with self._client_with_provider(_LLMErrorProvider()) as test_client:
            response = test_client.post("/api/analyze", json={"historia_clinica": valid_historia})
        assert "detail" in response.json()
