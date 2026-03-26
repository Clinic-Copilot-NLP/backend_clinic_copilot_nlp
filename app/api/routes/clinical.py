"""
Rutas de lectura de datos clínicos.

GET /patients/{patient_id}/summary — Resumen clínico completo (domains, alerts, timeline)
"""

import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.schemas.clinical import SummaryResponse
from app.core.services import clinical_data_service
from app.db.base import get_db

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/patients/{patient_id}/summary", response_model=SummaryResponse)
async def get_patient_summary(
    patient_id: str,
    db: AsyncSession = Depends(get_db),
) -> SummaryResponse:
    """
    Retorna el resumen clínico más reciente del paciente.

    Mapea los arreglos JSONB del análisis (domains, alerts, timeline)
    a los schemas de respuesta esperados por el frontend.

    Retorna 404 si no hay análisis disponible para el paciente.
    """
    analysis = await clinical_data_service.get_latest_analysis(db, patient_id)
    if analysis is None:
        raise HTTPException(
            status_code=404,
            detail="No hay análisis disponible para este paciente",
        )

    return await clinical_data_service.build_summary_response(analysis, patient_id)
