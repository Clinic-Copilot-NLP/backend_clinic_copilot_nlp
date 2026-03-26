"""
Tests unitarios para patient_service.
"""

import uuid
from unittest.mock import AsyncMock, MagicMock

from app.api.schemas.patient import PatientCreate
from app.core.services.patient_service import (
    create_patient,
    get_all_patients,
    get_patient_by_id,
)
from app.db.models.patient import Patient


def _make_mock_db() -> AsyncMock:
    """Construye un AsyncMock de AsyncSession básico."""
    db = AsyncMock()
    db.add = MagicMock()
    db.flush = AsyncMock()
    db.execute = AsyncMock()
    return db


def _make_patient_data() -> PatientCreate:
    """Datos válidos de paciente para tests."""
    return PatientCreate(name="María López", age=45, gender="F", specialty="Cardiología")


# ---------------------------------------------------------------------------
# create_patient
# ---------------------------------------------------------------------------


class TestCreatePatient:
    async def test_create_patient_calls_db_add(self):
        """create_patient() llama a db.add() con un objeto Patient."""
        db = _make_mock_db()
        data = _make_patient_data()
        await create_patient(db, data)

        db.add.assert_called_once()
        call_arg = db.add.call_args[0][0]
        assert isinstance(call_arg, Patient)

    async def test_create_patient_calls_db_flush(self):
        """create_patient() llama a db.flush() para obtener el ID."""
        db = _make_mock_db()
        data = _make_patient_data()
        await create_patient(db, data)
        db.flush.assert_called_once()

    async def test_create_patient_returns_patient_instance(self):
        """create_patient() retorna una instancia de Patient."""
        db = _make_mock_db()
        data = _make_patient_data()
        patient = await create_patient(db, data)
        assert isinstance(patient, Patient)

    async def test_create_patient_maps_name(self):
        """El nombre del paciente creado coincide con el input."""
        db = _make_mock_db()
        data = _make_patient_data()
        patient = await create_patient(db, data)
        assert patient.name == "María López"

    async def test_create_patient_maps_age(self):
        """La edad del paciente creado coincide con el input."""
        db = _make_mock_db()
        data = _make_patient_data()
        patient = await create_patient(db, data)
        assert patient.age == 45

    async def test_create_patient_maps_gender(self):
        """El género del paciente creado coincide con el input."""
        db = _make_mock_db()
        data = _make_patient_data()
        patient = await create_patient(db, data)
        assert patient.gender == "F"

    async def test_create_patient_maps_specialty(self):
        """La especialidad del paciente creado coincide con el input."""
        db = _make_mock_db()
        data = _make_patient_data()
        patient = await create_patient(db, data)
        assert patient.specialty == "Cardiología"

    async def test_create_patient_generates_uuid(self):
        """El ID del paciente creado es un UUID válido."""
        db = _make_mock_db()
        data = _make_patient_data()
        patient = await create_patient(db, data)
        assert isinstance(patient.id, uuid.UUID)


# ---------------------------------------------------------------------------
# get_all_patients
# ---------------------------------------------------------------------------


class TestGetAllPatients:
    async def test_get_all_patients_calls_db_execute(self):
        """get_all_patients() llama a db.execute()."""
        db = _make_mock_db()
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        db.execute = AsyncMock(return_value=mock_result)

        await get_all_patients(db)
        assert db.execute.called

    async def test_get_all_patients_returns_list(self):
        """get_all_patients() retorna una lista."""
        db = _make_mock_db()
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        db.execute = AsyncMock(return_value=mock_result)

        result = await get_all_patients(db)
        assert isinstance(result, list)

    async def test_get_all_patients_returns_patients_when_found(self):
        """get_all_patients() retorna los pacientes cuando los hay."""
        db = _make_mock_db()
        patient_mock = MagicMock(spec=Patient)

        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [patient_mock]
        db.execute = AsyncMock(return_value=mock_result)

        result = await get_all_patients(db)
        assert len(result) == 1
        assert result[0] is patient_mock

    async def test_get_all_patients_executes_once(self):
        """get_all_patients() solo llama a db.execute() una vez (sin filtro de fecha)."""
        db = _make_mock_db()
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        db.execute = AsyncMock(return_value=mock_result)

        await get_all_patients(db)
        assert db.execute.call_count == 1


# ---------------------------------------------------------------------------
# get_patient_by_id
# ---------------------------------------------------------------------------


class TestGetPatientById:
    async def test_get_patient_by_id_returns_patient_when_found(self):
        """get_patient_by_id() retorna el paciente si existe."""
        db = _make_mock_db()
        patient_mock = MagicMock(spec=Patient)
        patient_id = "11111111-1111-1111-1111-111111111111"

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = patient_mock
        db.execute = AsyncMock(return_value=mock_result)

        result = await get_patient_by_id(db, patient_id)
        assert result is patient_mock

    async def test_get_patient_by_id_returns_none_when_not_found(self):
        """get_patient_by_id() retorna None si el paciente no existe."""
        db = _make_mock_db()
        patient_id = "99999999-9999-9999-9999-999999999999"

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        db.execute = AsyncMock(return_value=mock_result)

        result = await get_patient_by_id(db, patient_id)
        assert result is None

    async def test_get_patient_by_id_calls_db_execute(self):
        """get_patient_by_id() llama a db.execute() una vez."""
        db = _make_mock_db()
        patient_id = "11111111-1111-1111-1111-111111111111"

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        db.execute = AsyncMock(return_value=mock_result)

        await get_patient_by_id(db, patient_id)
        db.execute.assert_called_once()
