"""
Tests unitarios para clinical_data_service.
"""

from unittest.mock import AsyncMock, MagicMock

from app.api.schemas.clinical import (
    AlertItem,
    DomainItem,
    SummaryResponse,
    TimelineItem,
)
from app.core.services.clinical_data_service import (
    build_summary_response,
    get_latest_analysis,
)


def _make_mock_db() -> AsyncMock:
    """Construye un AsyncMock de AsyncSession básico."""
    db = AsyncMock()
    db.execute = AsyncMock()
    return db


def _make_analysis_mock(
    domains: list | None = None,
    alerts: list | None = None,
    timeline: list | None = None,
) -> MagicMock:
    """Construye un mock de ClinicalAnalysis con valores por defecto."""
    analysis = MagicMock()
    analysis.domains = domains if domains is not None else []
    analysis.alerts = alerts if alerts is not None else []
    analysis.timeline = timeline if timeline is not None else []
    return analysis


# ---------------------------------------------------------------------------
# get_latest_analysis
# ---------------------------------------------------------------------------


class TestGetLatestAnalysis:
    async def test_get_latest_analysis_returns_analysis_when_found(self):
        """Retorna el análisis cuando existe."""
        db = _make_mock_db()
        analysis_mock = _make_analysis_mock()

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = analysis_mock
        db.execute = AsyncMock(return_value=mock_result)

        result = await get_latest_analysis(db, "11111111-1111-1111-1111-111111111111")
        assert result is analysis_mock

    async def test_get_latest_analysis_returns_none_when_not_found(self):
        """Retorna None cuando no hay análisis para el paciente."""
        db = _make_mock_db()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        db.execute = AsyncMock(return_value=mock_result)

        result = await get_latest_analysis(db, "99999999-9999-9999-9999-999999999999")
        assert result is None

    async def test_get_latest_analysis_calls_db_execute(self):
        """Llama a db.execute() una vez."""
        db = _make_mock_db()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        db.execute = AsyncMock(return_value=mock_result)

        await get_latest_analysis(db, "11111111-1111-1111-1111-111111111111")
        db.execute.assert_called_once()


# ---------------------------------------------------------------------------
# build_summary_response
# ---------------------------------------------------------------------------


class TestBuildSummaryResponse:
    async def test_returns_summary_response_instance(self):
        """Retorna una instancia de SummaryResponse."""
        analysis = _make_analysis_mock()
        result = await build_summary_response(analysis, "11111111-1111-1111-1111-111111111111")
        assert isinstance(result, SummaryResponse)

    async def test_patient_id_mapped_correctly(self):
        """patient_id en la respuesta coincide con el argumento."""
        patient_id = "11111111-1111-1111-1111-111111111111"
        analysis = _make_analysis_mock()
        result = await build_summary_response(analysis, patient_id)
        assert result.patient_id == patient_id

    async def test_domains_populated_from_analysis(self):
        """domains tiene 1 ítem cuando hay datos."""
        domains_data = [{"title": "Cardiología", "status": "ok", "description": "Estable."}]
        analysis = _make_analysis_mock(domains=domains_data)
        result = await build_summary_response(analysis, "11111111-1111-1111-1111-111111111111")
        assert len(result.domains) == 1
        assert isinstance(result.domains[0], DomainItem)
        assert result.domains[0].title == "Cardiología"
        assert result.domains[0].status == "ok"
        assert result.domains[0].description == "Estable."

    async def test_alerts_populated_from_analysis(self):
        """alerts tiene ítems cuando hay datos."""
        alerts_data = [
            {"title": "HbA1c elevada", "status": "warn", "description": "Requiere ajuste"}
        ]
        analysis = _make_analysis_mock(alerts=alerts_data)
        result = await build_summary_response(analysis, "11111111-1111-1111-1111-111111111111")
        assert len(result.alerts) == 1
        assert isinstance(result.alerts[0], AlertItem)
        assert result.alerts[0].title == "HbA1c elevada"
        assert result.alerts[0].status == "warn"

    async def test_timeline_populated_from_analysis(self):
        """timeline tiene ítems cuando hay datos."""
        timeline_data = [
            {
                "date": "2018-05-10",
                "title": "Diagnóstico",
                "description": "Primera consulta.",
                "is_critical": False,
            }
        ]
        analysis = _make_analysis_mock(timeline=timeline_data)
        result = await build_summary_response(analysis, "11111111-1111-1111-1111-111111111111")
        assert len(result.timeline) == 1
        assert isinstance(result.timeline[0], TimelineItem)
        assert result.timeline[0].title == "Diagnóstico"
        assert result.timeline[0].is_critical is False

    async def test_domains_empty_when_no_data(self):
        """domains vacío cuando la lista está vacía."""
        analysis = _make_analysis_mock(domains=[])
        result = await build_summary_response(analysis, "11111111-1111-1111-1111-111111111111")
        assert result.domains == []

    async def test_alerts_empty_when_no_data(self):
        """alerts vacío cuando la lista está vacía."""
        analysis = _make_analysis_mock(alerts=[])
        result = await build_summary_response(analysis, "11111111-1111-1111-1111-111111111111")
        assert result.alerts == []

    async def test_timeline_empty_when_no_data(self):
        """timeline vacío cuando la lista está vacía."""
        analysis = _make_analysis_mock(timeline=[])
        result = await build_summary_response(analysis, "11111111-1111-1111-1111-111111111111")
        assert result.timeline == []

    async def test_domain_item_uses_persisted_id_from_jsonb(self):
        """DomainItem usa el 'id' persistido en JSONB — no genera uno nuevo."""
        persisted_id = "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"
        domains_data = [
            {"id": persisted_id, "title": "Cardiología", "status": "ok", "description": "Estable."}
        ]
        analysis = _make_analysis_mock(domains=domains_data)
        result = await build_summary_response(analysis, "11111111-1111-1111-1111-111111111111")
        assert result.domains[0].id == persisted_id

    async def test_alert_item_uses_persisted_id_from_jsonb(self):
        """AlertItem usa el 'id' persistido en JSONB — no genera uno nuevo."""
        persisted_id = "cccccccc-cccc-cccc-cccc-cccccccccccc"
        alerts_data = [
            {"id": persisted_id, "title": "Test", "status": "warn", "description": "Desc."}
        ]
        analysis = _make_analysis_mock(alerts=alerts_data)
        result = await build_summary_response(analysis, "11111111-1111-1111-1111-111111111111")
        assert result.alerts[0].id == persisted_id

    async def test_timeline_item_uses_persisted_id_from_jsonb(self):
        """TimelineItem usa el 'id' persistido en JSONB — no genera uno nuevo."""
        persisted_id = "eeeeeeee-eeee-eeee-eeee-eeeeeeeeeeee"
        timeline_data = [
            {
                "id": persisted_id,
                "date": "2020-01-01",
                "title": "Evento",
                "description": "Desc.",
                "is_critical": True,
            }
        ]
        analysis = _make_analysis_mock(timeline=timeline_data)
        result = await build_summary_response(analysis, "11111111-1111-1111-1111-111111111111")
        assert result.timeline[0].id == persisted_id

    async def test_domain_item_fallback_uuid_when_no_id_in_jsonb(self):
        """DomainItem genera UUID como fallback si el JSONB no tiene 'id' (datos legacy)."""
        import uuid as uuid_mod

        domains_data = [{"title": "Cardiología", "status": "ok", "description": "Estable."}]
        analysis = _make_analysis_mock(domains=domains_data)
        result = await build_summary_response(analysis, "11111111-1111-1111-1111-111111111111")
        assert len(result.domains) == 1
        uuid_mod.UUID(result.domains[0].id)  # debe ser UUID válido

    async def test_alert_item_fallback_uuid_when_no_id_in_jsonb(self):
        """AlertItem genera UUID como fallback si el JSONB no tiene 'id' (datos legacy)."""
        import uuid as uuid_mod

        alerts_data = [{"title": "Test", "status": "warn", "description": "Desc."}]
        analysis = _make_analysis_mock(alerts=alerts_data)
        result = await build_summary_response(analysis, "11111111-1111-1111-1111-111111111111")
        assert len(result.alerts) == 1
        uuid_mod.UUID(result.alerts[0].id)

    async def test_timeline_item_fallback_uuid_when_no_id_in_jsonb(self):
        """TimelineItem genera UUID como fallback si el JSONB no tiene 'id' (datos legacy)."""
        import uuid as uuid_mod

        timeline_data = [
            {"date": "2020-01-01", "title": "Evento", "description": "Desc.", "is_critical": True}
        ]
        analysis = _make_analysis_mock(timeline=timeline_data)
        result = await build_summary_response(analysis, "11111111-1111-1111-1111-111111111111")
        assert len(result.timeline) == 1
        uuid_mod.UUID(result.timeline[0].id)
