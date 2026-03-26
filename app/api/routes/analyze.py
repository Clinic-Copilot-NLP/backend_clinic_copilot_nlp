"""
Ruta de análisis clínico.

POST /patients/{patient_id}/analyze — Llama al LLM, persiste el resultado.
Retorna HTTP 204 (sin body) si el análisis se guardó correctamente.
"""

import logging

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.schemas.request import AnalyzeRequest
from app.core.services.patient_service import get_patient_by_id
from app.core.services.summarizer import ClinicalSummarizerService
from app.db.base import get_db
from app.infrastructure.llm.base import LLMProviderError

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post(
    "/patients/{patient_id}/analyze",
    status_code=204,
    responses={
        204: {"description": "Análisis guardado correctamente"},
        404: {"description": "Paciente no encontrado"},
        422: {"description": "Historia clínica inválida"},
        501: {"description": "Proveedor LLM no implementado"},
        503: {"description": "Error del proveedor LLM"},
    },
)
async def analyze_patient_history(
    patient_id: str,
    body: AnalyzeRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> Response:
    """
    Analiza la historia clínica de un paciente y persiste el resultado.

    - **patient_id**: UUID del paciente (path param)
    - **historia_clinica**: Texto libre de la historia clínica (10–50.000 caracteres)

    Retorna HTTP 204 si el análisis fue guardado. El resultado puede recuperarse
    posteriormente con GET /api/v1/patients/{patient_id}/summary.
    """
    # Verificar que el paciente existe
    patient = await get_patient_by_id(db, patient_id)
    if patient is None:
        raise HTTPException(
            status_code=404,
            detail=f"Patient {patient_id} not found",
        )

    provider = request.app.state.llm_provider
    service = ClinicalSummarizerService()

    try:
        await service.analyze(
            historia_clinica=body.historia_clinica,
            patient_id=patient_id,
            provider=provider,
            db=db,
        )
    except LLMProviderError as e:
        logger.error(f"Error del proveedor LLM: {e} | proveedor={e.provider}")
        raise HTTPException(
            status_code=503,
            detail=str(e),
        ) from e
    except NotImplementedError as e:
        logger.error(f"Proveedor LLM no implementado: {e}")
        raise HTTPException(
            status_code=501,
            detail=str(e),
        ) from e

    return Response(status_code=204)
