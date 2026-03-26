"""
Tests de integración para POST /api/v1/patients/{id}/analyze.
Respuesta exitosa: HTTP 204 (sin body).
"""

import uuid
from unittest.mock import AsyncMock, MagicMock

from fastapi.testclient import TestClient

from app.infrastructure.llm.base import LLMProvider, LLMProviderError, LLMResponse

PATIENT_ID = "11111111-1111-1111-1111-111111111111"
UNKNOWN_ID = "99999999-9999-9999-9999-999999999999"


# ---------------------------------------------------------------------------
# Provider fakes para inyección de errores
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
# Helpers para crear el TestClient con db mock configurado
# ---------------------------------------------------------------------------


def _make_patient_mock(patient_id: str = PATIENT_ID) -> MagicMock:
    """Crea un mock de Patient ORM."""
    patient = MagicMock()
    patient.id = uuid.UUID(patient_id)
    patient.name = "María López"
    patient.age = 45
    patient.gender = "F"
    patient.specialty = "Cardiología"
    return patient


def _make_db_mock_with_patient(patient_id: str = PATIENT_ID) -> AsyncMock:
    """
    Crea un AsyncMock de AsyncSession que simula un paciente existente.
    get_patient_by_id usa db.execute(...).scalar_one_or_none() para buscar paciente.
    """
    db = AsyncMock()
    db.add = MagicMock()
    db.flush = AsyncMock()
    db.commit = AsyncMock()
    db.rollback = AsyncMock()

    patient_mock = _make_patient_mock(patient_id)

    # Simular el resultado de db.execute() para get_patient_by_id
    found_result = MagicMock()
    found_result.scalar_one_or_none.return_value = patient_mock
    db.execute = AsyncMock(return_value=found_result)

    # db.get no es usado en la nueva versión del summarizer
    db.get = AsyncMock(return_value=None)

    return db


def _make_db_mock_without_patient() -> AsyncMock:
    """Crea un AsyncMock de AsyncSession que simula que el paciente NO existe."""
    db = AsyncMock()
    db.add = MagicMock()
    db.flush = AsyncMock()
    db.commit = AsyncMock()
    db.rollback = AsyncMock()
    db.get = AsyncMock(return_value=None)

    # db.execute retorna None para el scalar
    not_found_result = MagicMock()
    not_found_result.scalar_one_or_none.return_value = None
    db.execute = AsyncMock(return_value=not_found_result)

    return db


def _make_client_with_db(db_mock: AsyncMock, llm_provider=None):
    """
    Crea un TestClient con un mock de DB y un proveedor LLM inyectados.
    init_db se mockea para evitar conexión real a la base de datos en tests.
    Retorna un context manager.
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
            app.state.llm_provider = llm_provider or FakeLLMProvider()
            return self_inner._tc

        def __exit__(self_inner, *args):
            app.dependency_overrides.clear()
            self_inner._patch.stop()
            return self_inner._tc.__exit__(*args)

    return _ManagedClient()


# ---------------------------------------------------------------------------
# Happy path — 204
# ---------------------------------------------------------------------------


class TestAnalyzePatientHappyPath:
    def test_analyze_patient_exists_returns_204(self, valid_historia):
        """Paciente existente + LLM ok → HTTP 204."""
        db = _make_db_mock_with_patient()
        with _make_client_with_db(db) as client:
            response = client.post(
                f"/api/v1/patients/{PATIENT_ID}/analyze",
                json={"historia_clinica": valid_historia},
            )
        assert response.status_code == 204

    def test_analyze_patient_returns_empty_body(self, valid_historia):
        """HTTP 204 → body vacío."""
        db = _make_db_mock_with_patient()
        with _make_client_with_db(db) as client:
            response = client.post(
                f"/api/v1/patients/{PATIENT_ID}/analyze",
                json={"historia_clinica": valid_historia},
            )
        assert response.status_code == 204
        assert response.content == b""

    def test_analyze_persists_analysis(self, valid_historia):
        """db.add() es llamado para persistir el análisis."""
        db = _make_db_mock_with_patient()
        with _make_client_with_db(db) as client:
            client.post(
                f"/api/v1/patients/{PATIENT_ID}/analyze",
                json={"historia_clinica": valid_historia},
            )
        db.add.assert_called_once()


# ---------------------------------------------------------------------------
# Patient not found
# ---------------------------------------------------------------------------


class TestAnalyzePatientNotFound:
    def test_analyze_unknown_patient_returns_404(self, valid_historia):
        """UUID de paciente desconocido → HTTP 404."""
        db = _make_db_mock_without_patient()
        with _make_client_with_db(db) as client:
            response = client.post(
                f"/api/v1/patients/{UNKNOWN_ID}/analyze",
                json={"historia_clinica": valid_historia},
            )
        assert response.status_code == 404

    def test_analyze_unknown_patient_response_detail(self, valid_historia):
        """404 incluye 'detail' con mensaje sobre paciente no encontrado."""
        db = _make_db_mock_without_patient()
        with _make_client_with_db(db) as client:
            response = client.post(
                f"/api/v1/patients/{UNKNOWN_ID}/analyze",
                json={"historia_clinica": valid_historia},
            )
        data = response.json()
        assert "detail" in data
        assert "not found" in data["detail"].lower() or "Patient" in data["detail"]


# ---------------------------------------------------------------------------
# LLM errors
# ---------------------------------------------------------------------------


class TestAnalyzeLLMError:
    def test_analyze_llm_provider_error_returns_503(self, valid_historia):
        """LLMProviderError del proveedor → HTTP 503."""
        db = _make_db_mock_with_patient()
        with _make_client_with_db(db, _LLMErrorProvider()) as client:
            response = client.post(
                f"/api/v1/patients/{PATIENT_ID}/analyze",
                json={"historia_clinica": valid_historia},
            )
        assert response.status_code == 503

    def test_analyze_llm_error_response_has_detail(self, valid_historia):
        """503 incluye 'detail' en el body."""
        db = _make_db_mock_with_patient()
        with _make_client_with_db(db, _LLMErrorProvider()) as client:
            response = client.post(
                f"/api/v1/patients/{PATIENT_ID}/analyze",
                json={"historia_clinica": valid_historia},
            )
        assert "detail" in response.json()

    def test_analyze_not_implemented_provider_returns_501(self, valid_historia):
        """NotImplementedError del proveedor → HTTP 501."""
        db = _make_db_mock_with_patient()
        with _make_client_with_db(db, _NotImplementedProvider()) as client:
            response = client.post(
                f"/api/v1/patients/{PATIENT_ID}/analyze",
                json={"historia_clinica": valid_historia},
            )
        assert response.status_code == 501


# ---------------------------------------------------------------------------
# Input validation
# ---------------------------------------------------------------------------


class TestAnalyzeValidation:
    def test_analyze_historia_too_short_returns_422(self):
        """historia_clinica con menos de 10 chars → 422."""
        db = _make_db_mock_with_patient()
        with _make_client_with_db(db) as client:
            response = client.post(
                f"/api/v1/patients/{PATIENT_ID}/analyze",
                json={"historia_clinica": "corto"},
            )
        assert response.status_code == 422

    def test_analyze_historia_too_long_returns_422(self):
        """historia_clinica con 50.001 chars → 422."""
        db = _make_db_mock_with_patient()
        with _make_client_with_db(db) as client:
            response = client.post(
                f"/api/v1/patients/{PATIENT_ID}/analyze",
                json={"historia_clinica": "x" * 50_001},
            )
        assert response.status_code == 422

    def test_analyze_missing_body_returns_422(self):
        """Body vacío → 422."""
        db = _make_db_mock_with_patient()
        with _make_client_with_db(db) as client:
            response = client.post(
                f"/api/v1/patients/{PATIENT_ID}/analyze",
                json={},
            )
        assert response.status_code == 422

    def test_analyze_whitespace_only_returns_422(self):
        """Solo espacios en blanco → strip → demasiado corto → 422."""
        db = _make_db_mock_with_patient()
        with _make_client_with_db(db) as client:
            response = client.post(
                f"/api/v1/patients/{PATIENT_ID}/analyze",
                json={"historia_clinica": "   "},
            )
        assert response.status_code == 422
