from pydantic import BaseModel, Field, field_validator


class AnalyzeRequest(BaseModel):
    historia_clinica: str = Field(
        ...,
        min_length=10,
        max_length=50_000,
        description="Historia clínica del paciente en texto libre (español)",
    )

    @field_validator("historia_clinica", mode="before")
    @classmethod
    def strip_whitespace(cls, v: str) -> str:
        return v.strip()
