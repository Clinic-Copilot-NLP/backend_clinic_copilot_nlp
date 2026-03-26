"""
Servicio de gestión de pacientes.

Provee operaciones CRUD asíncronas sobre la tabla `patients`.
Todas las funciones reciben una `AsyncSession` como primer argumento
y no gestionan la transacción — la sesión es responsabilidad del caller.
"""

import logging
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.schemas.patient import PatientCreate
from app.db.models.patient import Patient

logger = logging.getLogger(__name__)


async def create_patient(db: AsyncSession, data: PatientCreate) -> Patient:
    """
    Crea un nuevo paciente en la base de datos.

    Genera un UUID para el id del paciente y hace flush para obtenerlo
    antes de retornar el objeto ORM.

    Args:
        db: Sesión asíncrona de SQLAlchemy.
        data: Datos validados del paciente a crear.

    Returns:
        Instancia de Patient con id asignado.
    """
    patient = Patient(
        id=uuid4(),
        name=data.name,
        age=data.age,
        gender=data.gender,
        specialty=data.specialty,
    )
    db.add(patient)
    await db.flush()
    logger.info(f"Patient created | id={patient.id} | name={patient.name}")
    return patient


async def get_all_patients(db: AsyncSession) -> list[Patient]:
    """
    Retorna todos los pacientes registrados en el sistema.

    Args:
        db: Sesión asíncrona de SQLAlchemy.

    Returns:
        Lista de pacientes ordenados por created_at ascendente.
    """
    stmt = select(Patient).order_by(Patient.created_at.asc())
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def get_patient_by_id(db: AsyncSession, patient_id: str) -> Patient | None:
    """
    Busca un paciente por su UUID.

    Args:
        db: Sesión asíncrona de SQLAlchemy.
        patient_id: UUID del paciente como string.

    Returns:
        Instancia de Patient si existe, None si no.
    """
    stmt = select(Patient).where(Patient.id == patient_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()
