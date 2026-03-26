"""
Tests unitarios para los proveedores stub (Ollama y HuggingFace).
"""

import pytest

from app.infrastructure.llm.ollama import OllamaProvider
from app.infrastructure.llm.huggingface import HuggingFaceProvider


class TestOllamaProvider:
    def test_ollama_provider_name(self):
        """provider_name retorna 'ollama'."""
        provider = OllamaProvider()
        assert provider.provider_name == "ollama"

    @pytest.mark.asyncio
    async def test_ollama_generate_raises(self):
        """generate() lanza NotImplementedError."""
        provider = OllamaProvider()
        with pytest.raises(NotImplementedError):
            await provider.generate("system", "user")


class TestHuggingFaceProvider:
    def test_huggingface_provider_name(self):
        """provider_name retorna 'huggingface'."""
        provider = HuggingFaceProvider()
        assert provider.provider_name == "huggingface"

    @pytest.mark.asyncio
    async def test_huggingface_generate_raises(self):
        """generate() lanza NotImplementedError."""
        provider = HuggingFaceProvider()
        with pytest.raises(NotImplementedError):
            await provider.generate("system", "user")
