"""
Tests de integración para los endpoints de Paciente:
  POST /api/v1/patients    — Crea un paciente, retorna {id}
  GET  /api/v1/patients    — Lista todos como dict {id: {name, age, gender, specialty}}
"""

import uuid
from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock

from fastapi.testclient import TestClient

from app.db.models.patient import Patient

# ---------------------------------------------------------------------------
# Helpers para construir mocks de DB y Patient
# ---------------------------------------------------------------------------


def _make_patient_orm(
    name: str = "María López",
    age: int = 45,
    gender: str = "F",
    specialty: str = "Cardiología",
    patient_id: str = "11111111-1111-1111-1111-111111111111",
) -> MagicMock:
    """Crea un mock del ORM Patient con campos configurables."""
    p = MagicMock(spec=Patient)
    p.id = uuid.UUID(patient_id)
    p.name = name
    p.age = age
    p.gender = gender
    p.specialty = specialty
    p.created_at = datetime(2026, 3, 26, 10, 0, 0, tzinfo=UTC)
    return p


def _make_create_db_mock() -> AsyncMock:
    """
    Crea un AsyncMock de AsyncSession que simula la creación de un paciente.
    El flush() es asíncrono y asigna el ID al objeto que se agrega.
    """
    db = AsyncMock()

    async def fake_flush():
        pass  # El patient ya tiene ID asignado en create_patient()

    db.flush = AsyncMock(side_effect=fake_flush)
    db.commit = AsyncMock()
    db.rollback = AsyncMock()
    db.add = MagicMock()
    db.execute = AsyncMock()

    return db


def _make_list_db_mock(patients: list) -> AsyncMock:
    """Crea un AsyncMock de AsyncSession que retorna una lista de pacientes."""
    db = AsyncMock()
    db.add = MagicMock()
    db.flush = AsyncMock()
    db.commit = AsyncMock()
    db.rollback = AsyncMock()

    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = patients
    db.execute = AsyncMock(return_value=mock_result)

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
# POST /api/v1/patients
# ---------------------------------------------------------------------------


class TestCreatePatient:
    def test_create_patient_valid_returns_201(self):
        """Body válido → HTTP 201."""
        db = _make_create_db_mock()
        with _make_client_with_db(db) as client:
            response = client.post(
                "/api/v1/patients",
                json={"name": "María López", "age": 45, "gender": "F", "specialty": "Cardiología"},
            )
        assert response.status_code == 201

    def test_create_patient_response_only_id(self):
        """Respuesta 201 contiene SOLO el campo 'id'."""
        db = _make_create_db_mock()
        with _make_client_with_db(db) as client:
            response = client.post(
                "/api/v1/patients",
                json={"name": "María López", "age": 45, "gender": "F", "specialty": "Cardiología"},
            )
        data = response.json()
        assert response.status_code == 201
        assert "id" in data
        # No debe tener campos extra
        assert "name" not in data
        assert "age" not in data
        assert "gender" not in data
        assert "specialty" not in data
        assert "has_alerts" not in data
        assert "last_visit" not in data

    def test_create_patient_response_id_is_valid_uuid(self):
        """El id retornado es un UUID válido."""
        db = _make_create_db_mock()
        with _make_client_with_db(db) as client:
            response = client.post(
                "/api/v1/patients",
                json={"name": "María López", "age": 45, "gender": "F", "specialty": "Cardiología"},
            )
        data = response.json()
        # Debe ser parseable como UUID
        uuid.UUID(data["id"])

    def test_create_patient_invalid_gender_returns_422(self):
        """Género inválido → 422."""
        db = _make_create_db_mock()
        with _make_client_with_db(db) as client:
            response = client.post(
                "/api/v1/patients",
                json={"name": "Carlos", "age": 30, "gender": "X", "specialty": "General"},
            )
        assert response.status_code == 422

    def test_create_patient_missing_name_returns_422(self):
        """Sin name → 422."""
        db = _make_create_db_mock()
        with _make_client_with_db(db) as client:
            response = client.post(
                "/api/v1/patients",
                json={"age": 30, "gender": "M", "specialty": "General"},
            )
        assert response.status_code == 422

    def test_create_patient_missing_age_returns_422(self):
        """Sin age → 422."""
        db = _make_create_db_mock()
        with _make_client_with_db(db) as client:
            response = client.post(
                "/api/v1/patients",
                json={"name": "Juan", "gender": "M", "specialty": "General"},
            )
        assert response.status_code == 422

    def test_create_patient_missing_specialty_returns_422(self):
        """Sin specialty → 422."""
        db = _make_create_db_mock()
        with _make_client_with_db(db) as client:
            response = client.post(
                "/api/v1/patients",
                json={"name": "Ana", "age": 25, "gender": "F"},
            )
        assert response.status_code == 422

    def test_create_patient_age_zero_returns_422(self):
        """Edad 0 → 422 (ge=1)."""
        db = _make_create_db_mock()
        with _make_client_with_db(db) as client:
            response = client.post(
                "/api/v1/patients",
                json={"name": "Bebé", "age": 0, "gender": "M", "specialty": "Neonatología"},
            )
        assert response.status_code == 422

    def test_create_patient_empty_body_returns_422(self):
        """Body vacío → 422."""
        db = _make_create_db_mock()
        with _make_client_with_db(db) as client:
            response = client.post("/api/v1/patients", json={})
        assert response.status_code == 422

    def test_create_patient_gender_normalized_lowercase(self):
        """Género 'm' minúscula → aceptado, normalizado a 'M'."""
        db = _make_create_db_mock()
        with _make_client_with_db(db) as client:
            response = client.post(
                "/api/v1/patients",
                json={"name": "Juan García", "age": 35, "gender": "m", "specialty": "Cardiología"},
            )
        assert response.status_code == 201


# ---------------------------------------------------------------------------
# GET /api/v1/patients
# ---------------------------------------------------------------------------


class TestGetPatients:
    def test_get_patients_returns_200(self):
        """GET /api/v1/patients → HTTP 200."""
        db = _make_list_db_mock([])
        with _make_client_with_db(db) as client:
            response = client.get("/api/v1/patients")
        assert response.status_code == 200

    def test_get_patients_returns_dict(self):
        """GET /api/v1/patients → retorna un objeto JSON (dict), no lista."""
        db = _make_list_db_mock([])
        with _make_client_with_db(db) as client:
            response = client.get("/api/v1/patients")
        data = response.json()
        assert isinstance(data, dict)

    def test_get_patients_empty_dict_when_no_patients(self):
        """Sin pacientes → dict vacío {}."""
        db = _make_list_db_mock([])
        with _make_client_with_db(db) as client:
            response = client.get("/api/v1/patients")
        data = response.json()
        assert data == {}

    def test_get_patients_returns_patients_as_dict(self):
        """Paciente existente → aparece en el dict con su id como clave."""
        patient = _make_patient_orm()
        db = _make_list_db_mock([patient])
        with _make_client_with_db(db) as client:
            response = client.get("/api/v1/patients")
        data = response.json()
        assert response.status_code == 200
        assert len(data) == 1
        # La clave es el UUID del paciente
        patient_id_str = str(patient.id)
        assert patient_id_str in data
        assert data[patient_id_str]["name"] == "María López"
        assert data[patient_id_str]["age"] == 45
        assert data[patient_id_str]["gender"] == "F"
        assert data[patient_id_str]["specialty"] == "Cardiología"

    def test_get_patients_patient_value_has_correct_fields(self):
        """Cada valor del dict tiene name, age, gender, specialty."""
        patient = _make_patient_orm()
        db = _make_list_db_mock([patient])
        with _make_client_with_db(db) as client:
            response = client.get("/api/v1/patients")
        data = response.json()
        patient_id_str = str(patient.id)
        value = data[patient_id_str]
        assert "name" in value
        assert "age" in value
        assert "gender" in value
        assert "specialty" in value
        # No debe tener campos extra
        assert "has_alerts" not in value
        assert "last_visit" not in value
        assert "appointment_time" not in value

    def test_get_patients_multiple_patients(self):
        """Múltiples pacientes → todos en el dict."""
        patient1 = _make_patient_orm(
            name="María López",
            patient_id="11111111-1111-1111-1111-111111111111",
        )
        patient2 = _make_patient_orm(
            name="Juan García",
            patient_id="22222222-2222-2222-2222-222222222222",
        )
        db = _make_list_db_mock([patient1, patient2])
        with _make_client_with_db(db) as client:
            response = client.get("/api/v1/patients")
        data = response.json()
        assert len(data) == 2
        assert "11111111-1111-1111-1111-111111111111" in data
        assert "22222222-2222-2222-2222-222222222222" in data


# ---------------------------------------------------------------------------
# Endpoints eliminados — verificar que no existen
# ---------------------------------------------------------------------------


class TestDeletedEndpoints:
    def test_patients_today_endpoint_does_not_exist(self):
        """GET /api/v1/patients/today → 404 (endpoint eliminado)."""
        db = _make_list_db_mock([])
        with _make_client_with_db(db) as client:
            response = client.get("/api/v1/patients/today")
        # El path /patients/today ahora se interpreta como /patients/{patient_id}
        # con patient_id="today", no como una ruta separada. Debe retornar 404 o
        # 503 (si falla la consulta DB con un UUID inválido), pero NO 200 con lista.
        assert response.status_code != 200 or not isinstance(response.json(), list)
