"""
Esquemas Pydantic para los recursos de análisis clínico.

Incluye items de dominio, alerta, timeline y el resumen clínico principal.
"""

from pydantic import BaseModel, Field

# ---------------------------------------------------------------------------
# Dominio clínico (GET /api/v1/patients/{id}/summary → domains[])
# ---------------------------------------------------------------------------


class DomainItem(BaseModel):
    id: str = Field(..., description="UUID generado por el servidor")
    title: str
    status: str = Field(..., description='"ok", "warn" o "danger"')
    description: str


# ---------------------------------------------------------------------------
# Alerta clínica (GET /api/v1/patients/{id}/summary → alerts[])
# ---------------------------------------------------------------------------


class AlertItem(BaseModel):
    id: str = Field(..., description="UUID generado por el servidor")
    title: str
    status: str = Field(..., description='"ok", "warn" o "danger"')
    description: str


# ---------------------------------------------------------------------------
# Evento de línea de tiempo (GET /api/v1/patients/{id}/summary → timeline[])
# ---------------------------------------------------------------------------


class TimelineItem(BaseModel):
    id: str = Field(..., description="UUID generado por el servidor")
    date: str = Field(..., description='Fecha "YYYY-MM-DD" o cadena vacía ""')
    title: str
    description: str
    is_critical: bool


# ---------------------------------------------------------------------------
# Respuesta principal del resumen
# ---------------------------------------------------------------------------


class SummaryResponse(BaseModel):
    patient_id: str
    domains: list[DomainItem]
    alerts: list[AlertItem]
    timeline: list[TimelineItem]
