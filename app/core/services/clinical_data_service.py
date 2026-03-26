"""
Servicio de lectura y transformación de datos clínicos.

Provee funciones para obtener el análisis clínico más reciente de un paciente
y transformarlo al formato que consume el frontend.
"""

import logging
from typing import Any
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.schemas.clinical import (
    AlertItem,
    DomainItem,
    SummaryResponse,
    TimelineItem,
)
from app.db.models.clinical_analysis import ClinicalAnalysis

logger = logging.getLogger(__name__)


async def get_latest_analysis(db: AsyncSession, patient_id: str) -> ClinicalAnalysis | None:
    """
    Obtiene el análisis clínico más reciente de un paciente.

    Args:
        db: Sesión asíncrona de SQLAlchemy.
        patient_id: UUID del paciente como string.

    Returns:
        El ClinicalAnalysis más reciente o None si no existe ninguno.
    """
    stmt = (
        select(ClinicalAnalysis)
        .where(ClinicalAnalysis.patient_id == patient_id)
        .order_by(ClinicalAnalysis.created_at.desc())
        .limit(1)
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def build_summary_response(analysis: ClinicalAnalysis, patient_id: str) -> SummaryResponse:
    """
    Transforma un ClinicalAnalysis en un SummaryResponse para el frontend.

    Mapea directamente los arreglos JSONB del análisis a los schemas de respuesta,
    generando un UUID por ítem como identificador de servidor.

    Args:
        analysis: El análisis clínico persistido.
        patient_id: UUID del paciente como string.

    Returns:
        SummaryResponse con domains, alerts y timeline.
    """
    raw_domains: list[Any] = analysis.domains or []
    raw_alerts: list[Any] = analysis.alerts or []
    raw_timeline: list[Any] = analysis.timeline or []

    domains: list[DomainItem] = []
    for item in raw_domains:
        try:
            domains.append(
                DomainItem(
                    id=item.get("id", str(uuid4())),
                    title=item.get("title", ""),
                    status=item.get("status", "ok"),
                    description=item.get("description", ""),
                )
            )
        except Exception as e:
            logger.warning(f"Failed to map domain item: {e} | data={item}")

    alerts: list[AlertItem] = []
    for item in raw_alerts:
        try:
            alerts.append(
                AlertItem(
                    id=item.get("id", str(uuid4())),
                    title=item.get("title", ""),
                    status=item.get("status", "ok"),
                    description=item.get("description", ""),
                )
            )
        except Exception as e:
            logger.warning(f"Failed to map alert item: {e} | data={item}")

    timeline: list[TimelineItem] = []
    for item in raw_timeline:
        try:
            timeline.append(
                TimelineItem(
                    id=item.get("id", str(uuid4())),
                    date=item.get("date", ""),
                    title=item.get("title", ""),
                    description=item.get("description", ""),
                    is_critical=bool(item.get("is_critical", False)),
                )
            )
        except Exception as e:
            logger.warning(f"Failed to map timeline item: {e} | data={item}")

    return SummaryResponse(
        patient_id=patient_id,
        domains=domains,
        alerts=alerts,
        timeline=timeline,
    )
