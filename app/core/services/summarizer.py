"""
Servicio de análisis clínico.

Orquesta la construcción de prompts, la llamada al proveedor LLM,
el parseo estructurado de la respuesta y la persistencia en base de datos.
"""

import json
import logging
import re
import time
from uuid import uuid4

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.prompts.clinical import SYSTEM_PROMPT, build_user_prompt
from app.db.models.clinical_analysis import ClinicalAnalysis
from app.infrastructure.llm.base import LLMProvider

logger = logging.getLogger(__name__)


def _parse_clinical_response(content: str) -> dict:
    """
    Parsea el contenido de la respuesta LLM al formato clínico estructurado.

    Intenta parsear el JSON completo primero. Si falla, intenta extraer
    cada sección (domains, alerts, timeline) de forma independiente con regex.
    Nunca lanza excepción — siempre retorna un dict con las 3 claves.

    Args:
        content: Texto de la respuesta del LLM.

    Returns:
        Dict con claves "domains", "alerts", "timeline". Cada valor es una lista
        (puede ser vacía si el parseo de esa sección falla).
    """
    # Limpiar posible markdown del LLM (```json ... ```)
    cleaned = content.strip()
    if cleaned.startswith("```"):
        lines = cleaned.split("\n")
        start_idx = 1 if lines[0].startswith("```") else 0
        end_idx = len(lines) - 1 if lines[-1].strip() == "```" else len(lines)
        cleaned = "\n".join(lines[start_idx:end_idx]).strip()

    # Intento 1: parsear el JSON completo
    try:
        data = json.loads(cleaned)
        result: dict = {}
        for key in ("domains", "alerts", "timeline"):
            raw = data.get(key)
            result[key] = raw if isinstance(raw, list) else []
        logger.debug("Respuesta LLM parseada exitosamente como JSON completo.")
        return result
    except (json.JSONDecodeError, TypeError, AttributeError):
        logger.warning("No se pudo parsear el JSON completo. Intentando extracción por sección.")

    # Intento 2: extracción por sección con regex
    result = {}
    for key in ("domains", "alerts", "timeline"):
        try:
            pattern = rf'"{key}"\s*:\s*(\[.*?\])'
            match = re.search(pattern, cleaned, re.DOTALL)
            if match:
                section_data = json.loads(match.group(1))
                result[key] = section_data if isinstance(section_data, list) else []
            else:
                result[key] = []
        except (json.JSONDecodeError, TypeError):
            logger.warning(f"No se pudo extraer la sección '{key}' de la respuesta LLM.")
            result[key] = []

    return result


class ClinicalSummarizerService:
    """
    Servicio de análisis clínico que orquesta la construcción de prompts,
    la llamada al proveedor LLM, el parseo estructurado de la respuesta
    y la persistencia del análisis en la base de datos.
    """

    async def analyze(
        self,
        historia_clinica: str,
        patient_id: str,
        provider: LLMProvider,
        db: AsyncSession,
    ) -> None:
        """
        Analiza una historia clínica, persiste el resultado y retorna None.

        Args:
            historia_clinica: Texto de la historia clínica del paciente.
            patient_id: UUID del paciente como string.
            provider: Implementación concreta del proveedor LLM.
            db: Sesión asíncrona de SQLAlchemy (el caller gestiona commit/rollback).
        """
        user_prompt = build_user_prompt(historia_clinica)

        logger.info(
            f"Iniciando análisis clínico | proveedor={provider.provider_name} "
            f"| patient_id={patient_id} | chars={len(historia_clinica)}"
        )

        start_time = time.monotonic()
        llm_response = await provider.generate(SYSTEM_PROMPT, user_prompt)
        elapsed_ms = int((time.monotonic() - start_time) * 1000)

        logger.info(
            f"Análisis completado | proveedor={provider.provider_name} "
            f"| tiempo={elapsed_ms}ms "
            f"| tokens_entrada={llm_response.tokens_input} "
            f"| tokens_salida={llm_response.tokens_output}"
        )

        parsed = _parse_clinical_response(llm_response.content)

        # Añadir UUID estable a cada ítem antes de persistir
        for key in ("domains", "alerts", "timeline"):
            for item in parsed.get(key, []):
                if isinstance(item, dict) and "id" not in item:
                    item["id"] = str(uuid4())

        analysis = ClinicalAnalysis(
            patient_id=patient_id,
            domains=parsed.get("domains", []),
            alerts=parsed.get("alerts", []),
            timeline=parsed.get("timeline", []),
            raw_llm_response=llm_response.content,
            proveedor=llm_response.provider,
            modelo=llm_response.model,
            tokens_entrada=llm_response.tokens_input,
            tokens_salida=llm_response.tokens_output,
            tiempo_procesamiento_ms=elapsed_ms,
        )

        db.add(analysis)
        await db.flush()

        logger.info(f"Análisis clínico persistido | patient_id={patient_id}")
