"""
Esquemas Pydantic para el recurso Paciente.

PatientCreate: datos requeridos para crear un paciente.
PatientCreateResponse: respuesta mínima con solo el ID generado.
"""

from pydantic import BaseModel, Field, field_validator


class PatientCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200, description="Nombre completo del paciente")
    age: int = Field(..., ge=1, le=150, description="Edad del paciente en años")
    gender: str = Field(..., description='Sexo del paciente: "M" o "F"')
    specialty: str = Field(
        ..., min_length=1, max_length=100, description="Especialidad médica de la consulta"
    )

    @field_validator("gender", mode="before")
    @classmethod
    def validate_gender(cls, v: str) -> str:
        """Valida que el género sea M o F (mayúscula)."""
        if not isinstance(v, str):
            raise ValueError("El género debe ser una cadena de texto")
        normalized = v.strip().upper()
        if normalized not in ("M", "F"):
            raise ValueError('El género debe ser "M" o "F"')
        return normalized


class PatientCreateResponse(BaseModel):
    id: str
