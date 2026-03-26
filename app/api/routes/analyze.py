import logging
from fastapi import APIRouter, HTTPException, Request

from app.api.schemas.request import AnalyzeRequest
from app.api.schemas.response import AnalyzeResponse
from app.core.services.summarizer import ClinicalSummarizerService
from app.infrastructure.llm.base import LLMProviderError

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze_clinical_history(
    body: AnalyzeRequest,
    request: Request,
) -> AnalyzeResponse:
    """
    Analiza una historia clínica en español y retorna un resumen ejecutivo técnico estructurado.

    - **historia_clinica**: Texto de la historia clínica del paciente (10–50.000 caracteres)

    Retorna un resumen estructurado con trayectoria clínica, intervenciones, estado de
    seguridad e impresión diagnóstica, junto con metadatos de tokens y tiempo de procesamiento.
    """
    provider = request.app.state.llm_provider
    service = ClinicalSummarizerService()

    try:
        return await service.analyze(body.historia_clinica, provider)
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
