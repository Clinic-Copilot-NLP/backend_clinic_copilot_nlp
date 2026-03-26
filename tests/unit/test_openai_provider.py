"""
Tests unitarios para OpenAIProvider.
Todos los tests mockean AsyncOpenAI — nunca se llama a la API real.
"""

from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest
from openai import APIConnectionError, APIError, RateLimitError

from app.infrastructure.llm.base import LLMProviderError, LLMResponse
from app.infrastructure.llm.openai_provider import OpenAIProvider


# ---------------------------------------------------------------------------
# Helpers para construir errores de openai correctamente
# ---------------------------------------------------------------------------


def _fake_request() -> httpx.Request:
    return httpx.Request("POST", "https://api.openai.com/v1/chat/completions")


def _fake_response(status_code: int = 429) -> httpx.Response:
    return httpx.Response(status_code, request=_fake_request())


def _make_rate_limit_error() -> RateLimitError:
    return RateLimitError(
        message="rate limit exceeded",
        response=_fake_response(429),
        body={},
    )


def _make_connection_error() -> APIConnectionError:
    return APIConnectionError(
        message="connect: connection refused",
        request=_fake_request(),
    )


def _make_api_error() -> APIError:
    return APIError(
        message="internal server error",
        request=_fake_request(),
        body={},
    )


# ---------------------------------------------------------------------------
# Fixture: proveedor con cliente mockeado
# ---------------------------------------------------------------------------


@pytest.fixture
def provider_and_mock(monkeypatch):
    """
    Retorna (OpenAIProvider, mock_client) con AsyncOpenAI parcheado.
    El mock_client.chat.completions.create es un AsyncMock configurable.
    """
    mock_client = MagicMock()
    mock_client.chat = MagicMock()
    mock_client.chat.completions = MagicMock()
    mock_client.chat.completions.create = AsyncMock()

    with patch("app.infrastructure.llm.openai_provider.AsyncOpenAI", return_value=mock_client):
        monkeypatch.setenv("OPENAI_API_KEY", "sk-fake-key-for-tests")
        monkeypatch.setenv("MODEL_NAME", "gpt-4o")
        from app.core.config import get_settings

        get_settings.cache_clear()
        settings = get_settings()
        prov = OpenAIProvider(settings)

    return prov, mock_client


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestOpenAIProvider:
    def test_provider_name(self, provider_and_mock):
        """provider_name retorna 'openai'."""
        prov, _ = provider_and_mock
        assert prov.provider_name == "openai"

    async def test_generate_happy_path(self, provider_and_mock):
        """Happy path: mock retorna completion correcto → LLMResponse válido."""
        prov, mock_client = provider_and_mock

        mock_usage = MagicMock()
        mock_usage.prompt_tokens = 150
        mock_usage.completion_tokens = 60

        mock_message = MagicMock()
        mock_message.content = '{"trayectoria_clinica": "test", "intervenciones_consolidadas": "test", "estado_seguridad": "test"}'

        mock_choice = MagicMock()
        mock_choice.message = mock_message

        mock_completion = MagicMock()
        mock_completion.choices = [mock_choice]
        mock_completion.usage = mock_usage

        mock_client.chat.completions.create.return_value = mock_completion

        result = await prov.generate("system prompt", "user prompt")

        assert isinstance(result, LLMResponse)
        assert result.provider == "openai"
        assert result.model == "gpt-4o"
        assert result.tokens_input == 150
        assert result.tokens_output == 60
        assert result.content == mock_message.content

    async def test_generate_usage_none(self, provider_and_mock):
        """usage=None → tokens_input y tokens_output son None."""
        prov, mock_client = provider_and_mock

        mock_message = MagicMock()
        mock_message.content = "respuesta sin usage"

        mock_choice = MagicMock()
        mock_choice.message = mock_message

        mock_completion = MagicMock()
        mock_completion.choices = [mock_choice]
        mock_completion.usage = None

        mock_client.chat.completions.create.return_value = mock_completion

        result = await prov.generate("system", "user")
        assert result.tokens_input is None
        assert result.tokens_output is None

    async def test_generate_content_none(self, provider_and_mock):
        """message.content = None → content == 'Sin respuesta'."""
        prov, mock_client = provider_and_mock

        mock_message = MagicMock()
        mock_message.content = None

        mock_choice = MagicMock()
        mock_choice.message = mock_message

        mock_completion = MagicMock()
        mock_completion.choices = [mock_choice]
        mock_completion.usage = None

        mock_client.chat.completions.create.return_value = mock_completion

        result = await prov.generate("system", "user")
        assert result.content == "Sin respuesta"

    async def test_generate_rate_limit_error(self, provider_and_mock):
        """RateLimitError → LLMProviderError con 'rate limit' en el mensaje."""
        prov, mock_client = provider_and_mock
        mock_client.chat.completions.create.side_effect = _make_rate_limit_error()

        with pytest.raises(LLMProviderError, match="rate limit"):
            await prov.generate("system", "user")

    async def test_generate_connection_error(self, provider_and_mock):
        """APIConnectionError → LLMProviderError con 'connect' en el mensaje."""
        prov, mock_client = provider_and_mock
        mock_client.chat.completions.create.side_effect = _make_connection_error()

        with pytest.raises(LLMProviderError, match="connect"):
            await prov.generate("system", "user")

    async def test_generate_api_error(self, provider_and_mock):
        """APIError → LLMProviderError."""
        prov, mock_client = provider_and_mock
        mock_client.chat.completions.create.side_effect = _make_api_error()

        with pytest.raises(LLMProviderError):
            await prov.generate("system", "user")

    async def test_generate_unexpected_error(self, provider_and_mock):
        """Exception genérica → LLMProviderError."""
        prov, mock_client = provider_and_mock
        mock_client.chat.completions.create.side_effect = Exception("boom")

        with pytest.raises(LLMProviderError):
            await prov.generate("system", "user")

    async def test_generate_exception_chain_preserved(self, provider_and_mock):
        """__cause__ debe ser la excepción original (raise ... from e)."""
        prov, mock_client = provider_and_mock
        original = Exception("causa original")
        mock_client.chat.completions.create.side_effect = original

        with pytest.raises(LLMProviderError) as exc_info:
            await prov.generate("system", "user")

        assert exc_info.value.__cause__ is original
