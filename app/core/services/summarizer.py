import json
import logging
import time

from app.api.schemas.response import AnalyzeResponse, ResumenEjecutivoTecnico
from app.core.prompts.clinical import SYSTEM_PROMPT, build_user_prompt
from app.infrastructure.llm.base import LLMProvider

logger = logging.getLogger(__name__)


class ClinicalSummarizerService:
    """
    Servicio de análisis clínico que orquesta la construcción de prompts,
    la llamada al proveedor LLM y el parseo estructurado de la respuesta.
    """

    async def analyze(
        self, historia_clinica: str, provider: LLMProvider
    ) -> AnalyzeResponse:
        """
        Analiza una historia clínica y retorna un resumen ejecutivo técnico estructurado.

        Args:
            historia_clinica: Texto de la historia clínica del paciente.
            provider: Implementación concreta del proveedor LLM.

        Returns:
            AnalyzeResponse con el resumen estructurado, metadatos de tokens y timing.
        """
        user_prompt = build_user_prompt(historia_clinica)

        logger.info(
            f"Iniciando análisis clínico | proveedor={provider.provider_name} "
            f"| chars={len(historia_clinica)}"
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

        resumen_ejecutivo = self._parse_llm_response(llm_response.content)

        return AnalyzeResponse(
            resumen_ejecutivo=resumen_ejecutivo,
            proveedor=llm_response.provider,
            modelo=llm_response.model,
            tokens_entrada=llm_response.tokens_input,
            tokens_salida=llm_response.tokens_output,
            tiempo_procesamiento_ms=elapsed_ms,
        )

    def _parse_llm_response(self, content: str) -> ResumenEjecutivoTecnico | None:
        """
        Intenta parsear el contenido de la respuesta LLM como JSON estructurado.

        Si el parseo es exitoso, retorna ResumenEjecutivoTecnico.
        Si falla, degrada gracefully: retorna None y loguea el error.
        """
        try:
            # Limpiar posible markdown del LLM (```json ... ```)
            cleaned = content.strip()
            if cleaned.startswith("```"):
                lines = cleaned.split("\n")
                start_idx = 1 if lines[0].startswith("```") else 0
                end_idx = len(lines) - 1 if lines[-1].strip() == "```" else len(lines)
                cleaned = "\n".join(lines[start_idx:end_idx]).strip()

            data = json.loads(cleaned)
            resumen = ResumenEjecutivoTecnico(**data)
            logger.debug("Respuesta LLM parseada exitosamente como JSON estructurado.")
            return resumen

        except (json.JSONDecodeError, KeyError, TypeError, ValueError) as e:
            logger.warning(
                f"No se pudo parsear la respuesta LLM como JSON estructurado: {e}."
            )
            return None
