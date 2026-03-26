"""
Tests unitarios para ClinicalSummarizerService.

El servicio ahora acepta patient_id y db como argumentos adicionales,
persiste el análisis y retorna None (HTTP 204).
"""

import json
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.core.services.summarizer import ClinicalSummarizerService
from app.infrastructure.llm.base import LLMProvider, LLMProviderError, LLMResponse

# ---------------------------------------------------------------------------
# Helpers / fakes locales
# ---------------------------------------------------------------------------

VALID_JSON_CONTENT = json.dumps(
    {
        "domains": [
            {"title": "Cardiología - HTA", "status": "warn", "description": "HTA estadio 2."}
        ],
        "alerts": [
            {"title": "Uso de AINEs contraindicado", "status": "danger", "description": "IRC."}
        ],
        "timeline": [
            {
                "date": "2018-05-10",
                "title": "Diagnóstico HTA",
                "description": "Primera consulta.",
                "is_critical": False,
            }
        ],
    }
)

MARKDOWN_FENCED_JSON = f"```json\n{VALID_JSON_CONTENT}\n```"

PATIENT_ID = "11111111-1111-1111-1111-111111111111"


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


def _make_db_mock() -> AsyncMock:
    """Crea un AsyncMock de AsyncSession para tests del servicio."""
    db = AsyncMock()
    db.add = MagicMock()
    db.flush = AsyncMock()
    db.commit = AsyncMock()
    db.rollback = AsyncMock()
    return db


# ---------------------------------------------------------------------------
# Tests del método analyze()
# ---------------------------------------------------------------------------


class TestAnalyze:
    async def test_analyze_returns_none(self):
        """analyze() retorna None (HTTP 204 — sin body)."""
        service = ClinicalSummarizerService()
        db = _make_db_mock()
        result = await service.analyze(
            "Historia clínica de prueba.", PATIENT_ID, _FakeProvider(), db
        )
        assert result is None

    async def test_analyze_calls_db_add(self):
        """analyze() llama db.add() para persistir el ClinicalAnalysis."""
        service = ClinicalSummarizerService()
        db = _make_db_mock()
        await service.analyze("Historia clínica de prueba.", PATIENT_ID, _FakeProvider(), db)
        db.add.assert_called_once()

    async def test_analyze_calls_db_flush(self):
        """analyze() llama db.flush() después de db.add()."""
        service = ClinicalSummarizerService()
        db = _make_db_mock()
        await service.analyze("Historia clínica de prueba.", PATIENT_ID, _FakeProvider(), db)
        db.flush.assert_called_once()

    async def test_analyze_persists_clinical_analysis_object(self):
        """db.add() recibe una instancia de ClinicalAnalysis."""
        from app.db.models.clinical_analysis import ClinicalAnalysis

        service = ClinicalSummarizerService()
        db = _make_db_mock()
        await service.analyze("Historia clínica de prueba.", PATIENT_ID, _FakeProvider(), db)
        added_obj = db.add.call_args[0][0]
        assert isinstance(added_obj, ClinicalAnalysis)

    async def test_analyze_propagates_llm_provider_error(self):
        """analyze() propaga LLMProviderError si el proveedor falla."""
        service = ClinicalSummarizerService()
        db = _make_db_mock()
        with pytest.raises(LLMProviderError):
            await service.analyze("Historia clínica de prueba.", PATIENT_ID, _ErrorProvider(), db)

    async def test_analyze_domains_persisted_with_ids(self):
        """Los ítems de domains en el análisis persistido tienen campo 'id'."""
        from app.db.models.clinical_analysis import ClinicalAnalysis

        service = ClinicalSummarizerService()
        db = _make_db_mock()
        await service.analyze("Historia clínica de prueba.", PATIENT_ID, _FakeProvider(), db)
        added_obj: ClinicalAnalysis = db.add.call_args[0][0]
        assert added_obj.domains is not None
        assert len(added_obj.domains) > 0
        for item in added_obj.domains:
            assert "id" in item

    async def test_analyze_alerts_persisted_with_ids(self):
        """Los ítems de alerts en el análisis persistido tienen campo 'id'."""
        from app.db.models.clinical_analysis import ClinicalAnalysis

        service = ClinicalSummarizerService()
        db = _make_db_mock()
        await service.analyze("Historia clínica de prueba.", PATIENT_ID, _FakeProvider(), db)
        added_obj: ClinicalAnalysis = db.add.call_args[0][0]
        assert added_obj.alerts is not None
        assert len(added_obj.alerts) > 0
        for item in added_obj.alerts:
            assert "id" in item

    async def test_analyze_timeline_persisted_with_ids(self):
        """Los ítems de timeline en el análisis persistido tienen campo 'id'."""
        from app.db.models.clinical_analysis import ClinicalAnalysis

        service = ClinicalSummarizerService()
        db = _make_db_mock()
        await service.analyze("Historia clínica de prueba.", PATIENT_ID, _FakeProvider(), db)
        added_obj: ClinicalAnalysis = db.add.call_args[0][0]
        assert added_obj.timeline is not None
        assert len(added_obj.timeline) > 0
        for item in added_obj.timeline:
            assert "id" in item

    async def test_analyze_does_not_add_id_if_llm_provides_one(self):
        """Si el LLM ya provee 'id' en un ítem, no se sobreescribe."""
        from app.db.models.clinical_analysis import ClinicalAnalysis

        llm_provided_id = "llm-provided-uuid-here"
        content = json.dumps(
            {
                "domains": [
                    {
                        "id": llm_provided_id,
                        "title": "Cardiología",
                        "status": "ok",
                        "description": "Estable.",
                    }
                ],
                "alerts": [],
                "timeline": [],
            }
        )
        service = ClinicalSummarizerService()
        db = _make_db_mock()
        await service.analyze(
            "Historia clínica de prueba.", PATIENT_ID, _FakeProvider(content=content), db
        )
        added_obj: ClinicalAnalysis = db.add.call_args[0][0]
        assert added_obj.domains[0]["id"] == llm_provided_id
