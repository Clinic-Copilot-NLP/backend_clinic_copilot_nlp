"""
Tests unitarios para ClinicalSummarizerService.
"""

import json

import pytest

from app.api.schemas.response import AnalyzeResponse, ResumenEjecutivoTecnico
from app.core.services.summarizer import ClinicalSummarizerService
from app.infrastructure.llm.base import LLMProvider, LLMProviderError, LLMResponse


# ---------------------------------------------------------------------------
# Helpers / fakes locales
# ---------------------------------------------------------------------------

VALID_JSON_CONTENT = json.dumps(
    {
        "trayectoria_clinica": "Paciente con HTA desde 2019.",
        "intervenciones_consolidadas": "Enalapril 10mg c/12h.",
        "estado_seguridad": "Alergia a penicilina.",
    }
)

MARKDOWN_FENCED_JSON = f"```json\n{VALID_JSON_CONTENT}\n```"


class _FakeProvider(LLMProvider):
    """Proveedor fake configurable para tests del servicio."""

    def __init__(
        self,
        content: str = VALID_JSON_CONTENT,
        tokens_input: int | None = 100,
        tokens_output: int | None = 50,
        model: str = "fake-model",
        provider_name_value: str = "fake",
    ) -> None:
        self._content = content
        self._tokens_input = tokens_input
        self._tokens_output = tokens_output
        self._model = model
        self._provider_name_value = provider_name_value

    @property
    def provider_name(self) -> str:
        return self._provider_name_value

    async def generate(self, system_prompt: str, user_prompt: str) -> LLMResponse:
        return LLMResponse(
            content=self._content,
            tokens_input=self._tokens_input,
            tokens_output=self._tokens_output,
            model=self._model,
            provider=self._provider_name_value,
        )


class _ErrorProvider(LLMProvider):
    """Proveedor fake que lanza LLMProviderError."""

    @property
    def provider_name(self) -> str:
        return "error-provider"

    async def generate(self, system_prompt: str, user_prompt: str) -> LLMResponse:
        raise LLMProviderError("Error simulado", self.provider_name)


# ---------------------------------------------------------------------------
# Tests del método analyze()
# ---------------------------------------------------------------------------


class TestAnalyze:
    async def test_analyze_returns_analyze_response(self):
        """analyze() retorna una instancia de AnalyzeResponse."""
        service = ClinicalSummarizerService()
        result = await service.analyze("Historia clínica de prueba.", _FakeProvider())
        assert isinstance(result, AnalyzeResponse)

    async def test_analyze_resumen_ejecutivo_populated(self):
        """resumen_ejecutivo debe estar poblado con los campos correctos."""
        service = ClinicalSummarizerService()
        result = await service.analyze("Historia clínica de prueba.", _FakeProvider())
        assert result.resumen_ejecutivo is not None
        assert result.resumen_ejecutivo.trayectoria_clinica == "Paciente con HTA desde 2019."
        assert result.resumen_ejecutivo.intervenciones_consolidadas == "Enalapril 10mg c/12h."
        assert result.resumen_ejecutivo.estado_seguridad == "Alergia a penicilina."

    async def test_analyze_tokens_mapped(self):
        """tokens_entrada y tokens_salida provienen de llm_response."""
        provider = _FakeProvider(tokens_input=123, tokens_output=456)
        service = ClinicalSummarizerService()
        result = await service.analyze("Historia clínica de prueba.", provider)
        assert result.tokens_entrada == 123
        assert result.tokens_salida == 456

    async def test_analyze_tiempo_procesamiento_non_negative(self):
        """tiempo_procesamiento_ms debe ser >= 0."""
        service = ClinicalSummarizerService()
        result = await service.analyze("Historia clínica de prueba.", _FakeProvider())
        assert result.tiempo_procesamiento_ms >= 0

    async def test_analyze_proveedor_and_modelo(self):
        """proveedor y modelo se mapean desde la respuesta LLM."""
        provider = _FakeProvider(provider_name_value="fake", model="fake-model")
        service = ClinicalSummarizerService()
        result = await service.analyze("Historia clínica de prueba.", provider)
        assert result.proveedor == "fake"
        assert result.modelo == "fake-model"

    async def test_analyze_propagates_llm_provider_error(self):
        """analyze() propaga LLMProviderError si el proveedor falla."""
        service = ClinicalSummarizerService()
        with pytest.raises(LLMProviderError):
            await service.analyze("Historia clínica de prueba.", _ErrorProvider())


# ---------------------------------------------------------------------------
# Tests del método _parse_llm_response()
# ---------------------------------------------------------------------------


class TestParseLLMResponse:
    def _service(self) -> ClinicalSummarizerService:
        return ClinicalSummarizerService()

    def test_parse_valid_json(self):
        """JSON válido → retorna ResumenEjecutivoTecnico."""
        result = self._service()._parse_llm_response(VALID_JSON_CONTENT)
        assert isinstance(result, ResumenEjecutivoTecnico)

    def test_parse_markdown_fenced_json(self):
        """JSON dentro de bloque ```json...``` → retorna ResumenEjecutivoTecnico."""
        result = self._service()._parse_llm_response(MARKDOWN_FENCED_JSON)
        assert isinstance(result, ResumenEjecutivoTecnico)

    def test_parse_invalid_json_returns_none(self):
        """String que no es JSON → retorna None (degradación graciosa)."""
        result = self._service()._parse_llm_response("not json at all")
        assert result is None

    def test_parse_missing_fields_returns_none(self):
        """JSON sin campos requeridos → retorna None."""
        result = self._service()._parse_llm_response('{"foo": "bar"}')
        assert result is None
