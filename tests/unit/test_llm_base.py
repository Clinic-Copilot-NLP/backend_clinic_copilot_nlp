"""
Tests unitarios para las clases base del módulo LLM.
"""

import pytest

from app.infrastructure.llm.base import LLMProvider, LLMProviderError, LLMResponse


class TestLLMProviderError:
    def test_llm_provider_error_stores_message(self):
        """str(exc) retorna el mensaje original."""
        exc = LLMProviderError("algo falló", "openai")
        assert str(exc) == "algo falló"

    def test_llm_provider_error_stores_provider(self):
        """exc.provider almacena el nombre del proveedor."""
        exc = LLMProviderError("error", "openai")
        assert exc.provider == "openai"

    def test_llm_provider_error_stores_original_error(self):
        """exc.original_error es la excepción original."""
        original = ValueError("causa raíz")
        exc = LLMProviderError("error envuelto", "openai", original)
        assert exc.original_error is original

    def test_llm_provider_error_no_original_error(self):
        """original_error=None es válido y no lanza error."""
        exc = LLMProviderError("solo mensaje", "openai", None)
        assert exc.original_error is None

    def test_llm_provider_is_abstract(self):
        """No se puede instanciar LLMProvider directamente."""
        with pytest.raises(TypeError):
            LLMProvider()  # type: ignore[abstract]


class TestLLMResponse:
    def test_llm_response_valid(self):
        """Construir LLMResponse con todos los campos → válido."""
        resp = LLMResponse(
            content="Respuesta del modelo",
            tokens_input=200,
            tokens_output=80,
            model="gpt-4o",
            provider="openai",
        )
        assert resp.content == "Respuesta del modelo"
        assert resp.tokens_input == 200
        assert resp.tokens_output == 80
        assert resp.model == "gpt-4o"
        assert resp.provider == "openai"

    def test_llm_response_optional_tokens(self):
        """tokens_input y tokens_output pueden ser None."""
        resp = LLMResponse(
            content="Sin uso de tokens reportado",
            tokens_input=None,
            tokens_output=None,
            model="local-model",
            provider="ollama",
        )
        assert resp.tokens_input is None
        assert resp.tokens_output is None
