"""
Tests unitarios para los schemas Pydantic de request y response.
"""

import pytest
from pydantic import ValidationError

from app.api.schemas.request import AnalyzeRequest
from app.api.schemas.response import AnalyzeResponse, ResumenEjecutivoTecnico


# ---------------------------------------------------------------------------
# AnalyzeRequest
# ---------------------------------------------------------------------------


class TestAnalyzeRequest:
    def test_valid_historia_min_length(self):
        """10 caracteres exactos → válido."""
        req = AnalyzeRequest(historia_clinica="a" * 10)
        assert req.historia_clinica == "a" * 10

    def test_valid_historia_max_length(self):
        """50.000 caracteres exactos → válido."""
        req = AnalyzeRequest(historia_clinica="a" * 50_000)
        assert len(req.historia_clinica) == 50_000

    def test_invalid_historia_too_short(self):
        """9 caracteres → ValidationError."""
        with pytest.raises(ValidationError):
            AnalyzeRequest(historia_clinica="a" * 9)

    def test_invalid_historia_too_long(self):
        """50.001 caracteres → ValidationError."""
        with pytest.raises(ValidationError):
            AnalyzeRequest(historia_clinica="a" * 50_001)

    def test_whitespace_stripping(self):
        """El validador strip_whitespace elimina espacios del borde."""
        req = AnalyzeRequest(historia_clinica="   " + "a" * 10 + "   ")
        assert req.historia_clinica == "a" * 10

    def test_whitespace_makes_too_short(self):
        """'  ab  ' → solo 2 chars reales → ValidationError después de strip."""
        with pytest.raises(ValidationError):
            AnalyzeRequest(historia_clinica="  ab  ")

    def test_missing_field(self):
        """Sin argumento → ValidationError."""
        with pytest.raises(ValidationError):
            AnalyzeRequest()  # type: ignore[call-arg]


# ---------------------------------------------------------------------------
# ResumenEjecutivoTecnico
# ---------------------------------------------------------------------------


class TestResumenEjecutivoTecnico:
    def test_valid_construction(self):
        """Los tres campos presentes → modelo válido."""
        resumen = ResumenEjecutivoTecnico(
            trayectoria_clinica="Evolución crónica desde 2019.",
            intervenciones_consolidadas="Enalapril 10mg c/12h.",
            estado_seguridad="Alergia a penicilina.",
        )
        assert resumen.trayectoria_clinica == "Evolución crónica desde 2019."
        assert resumen.intervenciones_consolidadas == "Enalapril 10mg c/12h."
        assert resumen.estado_seguridad == "Alergia a penicilina."

    def test_missing_required_field(self):
        """Omitir trayectoria_clinica → ValidationError."""
        with pytest.raises(ValidationError):
            ResumenEjecutivoTecnico(  # type: ignore[call-arg]
                intervenciones_consolidadas="Enalapril 10mg.",
                estado_seguridad="Sin alergias.",
            )


# ---------------------------------------------------------------------------
# AnalyzeResponse
# ---------------------------------------------------------------------------


class TestAnalyzeResponse:
    def _make_resumen(self) -> ResumenEjecutivoTecnico:
        return ResumenEjecutivoTecnico(
            trayectoria_clinica="Trayectoria de prueba.",
            intervenciones_consolidadas="Intervención de prueba.",
            estado_seguridad="Sin alertas.",
        )

    def test_full_response(self):
        """Construir con todos los campos incluyendo resumen anidado → válido."""
        resp = AnalyzeResponse(
            resumen_ejecutivo=self._make_resumen(),
            proveedor="openai",
            modelo="gpt-4o",
            tokens_entrada=100,
            tokens_salida=50,
            tiempo_procesamiento_ms=320,
        )
        assert resp.proveedor == "openai"
        assert resp.modelo == "gpt-4o"
        assert resp.tokens_entrada == 100
        assert resp.tokens_salida == 50
        assert resp.tiempo_procesamiento_ms == 320
        assert resp.resumen_ejecutivo is not None

    def test_resumen_none(self):
        """resumen_ejecutivo=None → degradación graciosa, modelo válido."""
        resp = AnalyzeResponse(
            resumen_ejecutivo=None,
            proveedor="openai",
            modelo="gpt-4o",
            tiempo_procesamiento_ms=100,
        )
        assert resp.resumen_ejecutivo is None

    def test_tokens_none(self):
        """tokens_entrada y tokens_salida opcionales → None válido."""
        resp = AnalyzeResponse(
            proveedor="openai",
            modelo="gpt-4o",
            tokens_entrada=None,
            tokens_salida=None,
            tiempo_procesamiento_ms=50,
        )
        assert resp.tokens_entrada is None
        assert resp.tokens_salida is None

    def test_tiempo_required(self):
        """Omitir tiempo_procesamiento_ms → ValidationError."""
        with pytest.raises(ValidationError):
            AnalyzeResponse(  # type: ignore[call-arg]
                proveedor="openai",
                modelo="gpt-4o",
            )
