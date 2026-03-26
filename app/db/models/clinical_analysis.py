import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import DateTime, ForeignKey, Index, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.db.models.patient import Patient


class ClinicalAnalysis(Base):
    """Modelo de análisis clínico para la tabla `clinical_analyses`."""

    __tablename__ = "clinical_analyses"

    __table_args__ = (
        Index("ix_clinical_analyses_patient_id", "patient_id"),
        Index("ix_clinical_analyses_created_at", "created_at"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=func.gen_random_uuid(),
    )
    patient_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("patients.id", ondelete="CASCADE"),
        nullable=False,
    )

    # Secciones estructuradas (JSONB) generadas por el LLM
    domains: Mapped[list[Any] | None] = mapped_column(JSONB, nullable=True, server_default="[]")
    alerts: Mapped[list[Any] | None] = mapped_column(JSONB, nullable=True, server_default="[]")
    timeline: Mapped[list[Any] | None] = mapped_column(JSONB, nullable=True, server_default="[]")

    # Respuesta cruda del LLM
    raw_llm_response: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Metadatos del proveedor LLM
    proveedor: Mapped[str | None] = mapped_column(String(50), nullable=True)
    modelo: Mapped[str | None] = mapped_column(String(100), nullable=True)
    tokens_entrada: Mapped[int | None] = mapped_column(Integer, nullable=True)
    tokens_salida: Mapped[int | None] = mapped_column(Integer, nullable=True)
    tiempo_procesamiento_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    # Relación: un análisis pertenece a un paciente
    patient: Mapped["Patient"] = relationship(
        "Patient",
        back_populates="clinical_analyses",
        lazy="select",
    )
