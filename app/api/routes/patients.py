"""
Rutas para el recurso Paciente.

POST /patients   — Crea un nuevo paciente (HTTP 201), retorna solo {id}
GET  /patients   — Lista todos los pacientes como dict {id: {name, age, gender, specialty}}
"""

import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.schemas.patient import PatientCreate, PatientCreateResponse
from app.core.services import patient_service
from app.db.base import get_db

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/patients", response_model=PatientCreateResponse, status_code=201)
async def create_patient(
    body: PatientCreate,
    db: AsyncSession = Depends(get_db),
) -> PatientCreateResponse:
    """
    Crea un nuevo paciente en el sistema.

    - **name**: Nombre completo del paciente (1–200 caracteres)
    - **age**: Edad en años (1–150)
    - **gender**: Sexo del paciente — "M" o "F"
    - **specialty**: Especialidad médica de la consulta

    Retorna únicamente el UUID generado por el servidor.
    """
    try:
        patient = await patient_service.create_patient(db, body)
        return PatientCreateResponse(id=str(patient.id))
    except SQLAlchemyError as e:
        logger.error(f"Database error creating patient: {e}")
        raise HTTPException(status_code=503, detail="Error al crear el paciente") from e


@router.get("/patients")
async def get_patients(
    db: AsyncSession = Depends(get_db),
) -> dict:
    """
    Retorna todos los pacientes registrados como un mapa {id: {name, age, gender, specialty}}.
    """
    try:
        patients = await patient_service.get_all_patients(db)
        return {
            str(p.id): {
                "name": p.name,
                "age": p.age,
                "gender": p.gender,
                "specialty": p.specialty,
            }
            for p in patients
        }
    except SQLAlchemyError as e:
        logger.error(f"Database error fetching patients: {e}")
        raise HTTPException(status_code=503, detail="Error al obtener los pacientes") from e
