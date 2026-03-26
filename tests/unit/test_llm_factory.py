"""
Tests unitarios para la factory de proveedores LLM.
"""

import pytest

from app.infrastructure.llm.factory import get_llm_provider
from app.infrastructure.llm.huggingface import HuggingFaceProvider
from app.infrastructure.llm.ollama import OllamaProvider
from app.infrastructure.llm.openai_provider import OpenAIProvider


class TestGetLLMProvider:
    def _get_settings_with_provider(self, monkeypatch, provider: str):
        """Helper: limpia caché, setea LLM_PROVIDER y retorna Settings fresco."""
        from app.core.config import get_settings

        monkeypatch.setenv("LLM_PROVIDER", provider)
        get_settings.cache_clear()
        return get_settings()

    def test_factory_openai(self, monkeypatch):
        """LLM_PROVIDER=openai → retorna OpenAIProvider."""
        settings = self._get_settings_with_provider(monkeypatch, "openai")
        provider = get_llm_provider(settings)
        assert isinstance(provider, OpenAIProvider)

    def test_factory_ollama(self, monkeypatch):
        """LLM_PROVIDER=ollama → retorna OllamaProvider."""
        settings = self._get_settings_with_provider(monkeypatch, "ollama")
        provider = get_llm_provider(settings)
        assert isinstance(provider, OllamaProvider)

    def test_factory_huggingface(self, monkeypatch):
        """LLM_PROVIDER=huggingface → retorna HuggingFaceProvider."""
        settings = self._get_settings_with_provider(monkeypatch, "huggingface")
        provider = get_llm_provider(settings)
        assert isinstance(provider, HuggingFaceProvider)

    def test_factory_unknown_raises(self, monkeypatch):
        """LLM_PROVIDER desconocido → ValueError."""
        settings = self._get_settings_with_provider(monkeypatch, "unknown_xyz")
        with pytest.raises(ValueError):
            get_llm_provider(settings)

    def test_factory_unknown_error_message(self, monkeypatch):
        """El mensaje del ValueError contiene el nombre del proveedor."""
        settings = self._get_settings_with_provider(monkeypatch, "unknown_xyz")
        with pytest.raises(ValueError, match="unknown_xyz"):
            get_llm_provider(settings)
