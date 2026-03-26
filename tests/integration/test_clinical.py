"""
Tests de integración para los endpoints de datos clínicos:
  GET /api/v1/patients/{id}/summary
"""

import uuid
from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock

from fastapi.testclient import TestClient

PATIENT_ID = "11111111-1111-1111-1111-111111111111"
UNKNOWN_ID = "99999999-9999-9999-9999-999999999999"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_analysis_mock(
    domains: list | None = None,
    alerts: list | None = None,
    timeline: list | None = None,
) -> MagicMock:
    """Crea un mock de ClinicalAnalysis con datos configurables."""
    analysis = MagicMock()
    analysis.id = uuid.UUID("22222222-2222-2222-2222-222222222222")
    analysis.patient_id = uuid.UUID(PATIENT_ID)
    analysis.domains = domains if domains is not None else []
    analysis.alerts = alerts if alerts is not None else []
    analysis.timeline = timeline if timeline is not None else []
    analysis.created_at = datetime(2026, 3, 26, 10, 0, 0, tzinfo=UTC)
    return analysis


def _make_db_with_analysis(analysis_mock) -> AsyncMock:
    """AsyncSession mock que devuelve un análisis para get_latest_analysis."""
    db = AsyncMock()
    db.add = MagicMock()
    db.flush = AsyncMock()
    db.commit = AsyncMock()
    db.rollback = AsyncMock()

    result_mock = MagicMock()
    result_mock.scalar_one_or_none.return_value = analysis_mock
    db.execute = AsyncMock(return_value=result_mock)

    return db


def _make_db_without_analysis() -> AsyncMock:
    """AsyncSession mock que devuelve None para get_latest_analysis (sin análisis)."""
    db = AsyncMock()
    db.add = MagicMock()
    db.flush = AsyncMock()
    db.commit = AsyncMock()
    db.rollback = AsyncMock()

    result_mock = MagicMock()
    result_mock.scalar_one_or_none.return_value = None
    db.execute = AsyncMock(return_value=result_mock)

    return db


def _make_client_with_db(db_mock: AsyncMock):
    """Context manager que devuelve TestClient con get_db sobrescrito.
    init_db se mockea para evitar conexión real a la base de datos en tests.
    """
    from unittest.mock import AsyncMock as _AsyncMock
    from unittest.mock import patch

    from app.db.base import get_db
    from app.main import app
    from tests.conftest import FakeLLMProvider

    async def override_get_db():
        yield db_mock

    app.dependency_overrides[get_db] = override_get_db

    class _ManagedClient:
        def __enter__(self_inner):
            self_inner._patch = patch("app.main.init_db", new=_AsyncMock())
            self_inner._patch.start()
            self_inner._tc = TestClient(app, raise_server_exceptions=False)
            self_inner._tc.__enter__()
            app.state.llm_provider = FakeLLMProvider()
            return self_inner._tc

        def __exit__(self_inner, *args):
            app.dependency_overrides.clear()
            self_inner._patch.stop()
            return self_inner._tc.__exit__(*args)

    return _ManagedClient()


# ---------------------------------------------------------------------------
# GET /api/v1/patients/{id}/summary
# ---------------------------------------------------------------------------


class TestGetPatientSummary:
    def test_summary_with_analysis_returns_200(self):
        """Análisis existente → HTTP 200."""
        analysis = _make_analysis_mock()
        db = _make_db_with_analysis(analysis)
        with _make_client_with_db(db) as client:
            response = client.get(f"/api/v1/patients/{PATIENT_ID}/summary")
        assert response.status_code == 200

    def test_summary_response_schema(self):
        """Respuesta 200 incluye patient_id, domains, alerts, timeline."""
        analysis = _make_analysis_mock()
        db = _make_db_with_analysis(analysis)
        with _make_client_with_db(db) as client:
            response = client.get(f"/api/v1/patients/{PATIENT_ID}/summary")
        data = response.json()
        assert "patient_id" in data
        assert "domains" in data
        assert "alerts" in data
        assert "timeline" in data

    def test_summary_response_no_old_fields(self):
        """Respuesta 200 NÃO inclui safety ni consult_history (campos eliminados)."""
        analysis = _make_analysis_mock()
        db = _make_db_with_analysis(analysis)
        with _make_client_with_db(db) as client:
            response = client.get(f"/api/v1/patients/{PATIENT_ID}/summary")
        data = response.json()
        assert "safety" not in data
        assert "consult_history" not in data

    def test_summary_patient_id_in_response(self):
        """patient_id en la respuesta coincide con el path param."""
        analysis = _make_analysis_mock()
        db = _make_db_with_analysis(analysis)
        with _make_client_with_db(db) as client:
            response = client.get(f"/api/v1/patients/{PATIENT_ID}/summary")
        data = response.json()
        assert data["patient_id"] == PATIENT_ID

    def test_summary_domains_populated_from_analysis(self):
        """domains tiene ítems cuando el análisis los tiene."""
        domains = [{"title": "Cardiología", "status": "ok", "description": "Estable."}]
        analysis = _make_analysis_mock(domains=domains)
        db = _make_db_with_analysis(analysis)
        with _make_client_with_db(db) as client:
            response = client.get(f"/api/v1/patients/{PATIENT_ID}/summary")
        data = response.json()
        assert len(data["domains"]) == 1
        assert data["domains"][0]["title"] == "Cardiología"

    def test_summary_alerts_populated_from_analysis(self):
        """alerts tiene ítems cuando el análisis los tiene."""
        alerts = [{"title": "HbA1c elevada", "status": "warn", "description": "Requiere ajuste."}]
        analysis = _make_analysis_mock(alerts=alerts)
        db = _make_db_with_analysis(analysis)
        with _make_client_with_db(db) as client:
            response = client.get(f"/api/v1/patients/{PATIENT_ID}/summary")
        data = response.json()
        assert len(data["alerts"]) == 1
        assert data["alerts"][0]["title"] == "HbA1c elevada"

    def test_summary_timeline_populated_from_analysis(self):
        """timeline tiene ítems cuando el análisis los tiene."""
        timeline = [
            {
                "date": "2018-05-10",
                "title": "Diagnóstico",
                "description": "Primera consulta.",
                "is_critical": False,
            }
        ]
        analysis = _make_analysis_mock(timeline=timeline)
        db = _make_db_with_analysis(analysis)
        with _make_client_with_db(db) as client:
            response = client.get(f"/api/v1/patients/{PATIENT_ID}/summary")
        data = response.json()
        assert len(data["timeline"]) == 1
        assert data["timeline"][0]["title"] == "Diagnóstico"

    def test_summary_domain_item_fields(self):
        """Cada domain item tiene id, title, status, description."""
        domains = [{"title": "Cardiología", "status": "ok", "description": "Estable."}]
        analysis = _make_analysis_mock(domains=domains)
        db = _make_db_with_analysis(analysis)
        with _make_client_with_db(db) as client:
            response = client.get(f"/api/v1/patients/{PATIENT_ID}/summary")
        data = response.json()
        item = data["domains"][0]
        assert "id" in item
        assert "title" in item
        assert "status" in item
        assert "description" in item
        uuid.UUID(item["id"])  # El id debe ser UUID válido

    def test_summary_alert_item_fields(self):
        """Cada alert item tiene id, title, status, description."""
        alerts = [{"title": "Alerta", "status": "warn", "description": "Desc."}]
        analysis = _make_analysis_mock(alerts=alerts)
        db = _make_db_with_analysis(analysis)
        with _make_client_with_db(db) as client:
            response = client.get(f"/api/v1/patients/{PATIENT_ID}/summary")
        data = response.json()
        item = data["alerts"][0]
        assert "id" in item
        assert "title" in item
        assert "status" in item
        assert "description" in item
        uuid.UUID(item["id"])

    def test_summary_timeline_item_fields(self):
        """Cada timeline item tiene id, date, title, description, is_critical."""
        timeline = [
            {
                "date": "2020-01-01",
                "title": "Evento",
                "description": "Desc.",
                "is_critical": True,
            }
        ]
        analysis = _make_analysis_mock(timeline=timeline)
        db = _make_db_with_analysis(analysis)
        with _make_client_with_db(db) as client:
            response = client.get(f"/api/v1/patients/{PATIENT_ID}/summary")
        data = response.json()
        item = data["timeline"][0]
        assert "id" in item
        assert "date" in item
        assert "title" in item
        assert "description" in item
        assert "is_critical" in item
        uuid.UUID(item["id"])

    def test_summary_no_analysis_returns_404(self):
        """Sin análisis → HTTP 404."""
        db = _make_db_without_analysis()
        with _make_client_with_db(db) as client:
            response = client.get(f"/api/v1/patients/{PATIENT_ID}/summary")
        assert response.status_code == 404

    def test_summary_no_analysis_has_detail(self):
        """404 incluye clave 'detail' en la respuesta."""
        db = _make_db_without_analysis()
        with _make_client_with_db(db) as client:
            response = client.get(f"/api/v1/patients/{PATIENT_ID}/summary")
        assert "detail" in response.json()

    def test_summary_domain_id_is_stable_across_reads(self):
        """El ID del domain item es el mismo en dos lecturas — proviene del JSONB."""
        persisted_id = "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"
        domains = [
            {
                "id": persisted_id,
                "title": "Cardiología",
                "status": "ok",
                "description": "Estable.",
            }
        ]
        analysis = _make_analysis_mock(domains=domains)
        db1 = _make_db_with_analysis(analysis)
        db2 = _make_db_with_analysis(analysis)

        with _make_client_with_db(db1) as client:
            r1 = client.get(f"/api/v1/patients/{PATIENT_ID}/summary")
        with _make_client_with_db(db2) as client:
            r2 = client.get(f"/api/v1/patients/{PATIENT_ID}/summary")

        id1 = r1.json()["domains"][0]["id"]
        id2 = r2.json()["domains"][0]["id"]
        assert id1 == persisted_id
        assert id2 == persisted_id
        assert id1 == id2

    def test_summary_alert_id_is_stable_across_reads(self):
        """El ID del alert item es el mismo en dos lecturas — proviene del JSONB."""
        persisted_id = "cccccccc-cccc-cccc-cccc-cccccccccccc"
        alerts = [
            {
                "id": persisted_id,
                "title": "Alerta",
                "status": "warn",
                "description": "Desc.",
            }
        ]
        analysis = _make_analysis_mock(alerts=alerts)
        db1 = _make_db_with_analysis(analysis)
        db2 = _make_db_with_analysis(analysis)

        with _make_client_with_db(db1) as client:
            r1 = client.get(f"/api/v1/patients/{PATIENT_ID}/summary")
        with _make_client_with_db(db2) as client:
            r2 = client.get(f"/api/v1/patients/{PATIENT_ID}/summary")

        id1 = r1.json()["alerts"][0]["id"]
        id2 = r2.json()["alerts"][0]["id"]
        assert id1 == persisted_id
        assert id2 == persisted_id
        assert id1 == id2

    def test_summary_timeline_id_is_stable_across_reads(self):
        """El ID del timeline item es el mismo en dos lecturas — proviene del JSONB."""
        persisted_id = "eeeeeeee-eeee-eeee-eeee-eeeeeeeeeeee"
        timeline = [
            {
                "id": persisted_id,
                "date": "2018-05-10",
                "title": "Diagnóstico",
                "description": "Primera consulta.",
                "is_critical": False,
            }
        ]
        analysis = _make_analysis_mock(timeline=timeline)
        db1 = _make_db_with_analysis(analysis)
        db2 = _make_db_with_analysis(analysis)

        with _make_client_with_db(db1) as client:
            r1 = client.get(f"/api/v1/patients/{PATIENT_ID}/summary")
        with _make_client_with_db(db2) as client:
            r2 = client.get(f"/api/v1/patients/{PATIENT_ID}/summary")

        id1 = r1.json()["timeline"][0]["id"]
        id2 = r2.json()["timeline"][0]["id"]
        assert id1 == persisted_id
        assert id2 == persisted_id
        assert id1 == id2


# ---------------------------------------------------------------------------
# Endpoints eliminados — verificar que no existen
# ---------------------------------------------------------------------------


class TestDeletedEndpoints:
    def _make_simple_client(self):
        """Crea un TestClient básico con init_db mockeado."""
        from unittest.mock import AsyncMock as _AsyncMock
        from unittest.mock import patch

        from app.db.base import get_db
        from app.main import app
        from tests.conftest import FakeLLMProvider

        db = AsyncMock()

        async def override_get_db():
            yield db

        app.dependency_overrides[get_db] = override_get_db

        class _ManagedClient:
            def __enter__(self_inner):
                self_inner._patch = patch("app.main.init_db", new=_AsyncMock())
                self_inner._patch.start()
                self_inner._tc = TestClient(app, raise_server_exceptions=False)
                self_inner._tc.__enter__()
                app.state.llm_provider = FakeLLMProvider()
                return self_inner._tc

            def __exit__(self_inner, *args):
                app.dependency_overrides.clear()
                self_inner._patch.stop()
                return self_inner._tc.__exit__(*args)

        return _ManagedClient()

    def test_alerts_endpoint_does_not_exist(self):
        """GET /api/v1/patients/{id}/alerts → 404 o 405 (endpoint eliminado)."""
        with self._make_simple_client() as client:
            response = client.get(f"/api/v1/patients/{PATIENT_ID}/alerts")
        assert response.status_code in (404, 405)

    def test_medications_endpoint_does_not_exist(self):
        """GET /api/v1/patients/{id}/medications → 404 o 405 (endpoint eliminado)."""
        with self._make_simple_client() as client:
            response = client.get(f"/api/v1/patients/{PATIENT_ID}/medications")
        assert response.status_code in (404, 405)

    def test_pending_endpoint_does_not_exist(self):
        """GET /api/v1/patients/{id}/pending → 404 o 405 (endpoint eliminado)."""
        with self._make_simple_client() as client:
            response = client.get(f"/api/v1/patients/{PATIENT_ID}/pending")
        assert response.status_code in (404, 405)
