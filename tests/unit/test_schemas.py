"""
Tests unitarios para los schemas Pydantic de request y response.
"""

import pytest
from pydantic import ValidationError

from app.api.schemas.clinical import AlertItem, DomainItem, SummaryResponse, TimelineItem
from app.api.schemas.request import AnalyzeRequest

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
# DomainItem
# ---------------------------------------------------------------------------


class TestDomainItem:
    def test_valid_construction(self):
        """Todos los campos presentes → modelo válido."""
        item = DomainItem(
            id="aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
            title="Cardiología - HTA",
            status="warn",
            description="HTA estadio 2.",
        )
        assert item.id == "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"
        assert item.title == "Cardiología - HTA"
        assert item.status == "warn"
        assert item.description == "HTA estadio 2."

    def test_missing_required_field(self):
        """Omitir 'title' → ValidationError."""
        with pytest.raises(ValidationError):
            DomainItem(  # type: ignore[call-arg]
                id="aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
                status="ok",
                description="Sin título.",
            )


# ---------------------------------------------------------------------------
# AlertItem
# ---------------------------------------------------------------------------


class TestAlertItem:
    def test_valid_construction(self):
        """Todos los campos presentes → modelo válido."""
        item = AlertItem(
            id="bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb",
            title="Interacción medicamentosa",
            status="danger",
            description="Riesgo de toxicidad renal.",
        )
        assert item.status == "danger"
        assert item.title == "Interacción medicamentosa"

    def test_missing_required_field(self):
        """Omitir 'id' → ValidationError."""
        with pytest.raises(ValidationError):
            AlertItem(  # type: ignore[call-arg]
                title="Alerta",
                status="warn",
                description="Desc.",
            )


# ---------------------------------------------------------------------------
# TimelineItem
# ---------------------------------------------------------------------------


class TestTimelineItem:
    def test_valid_construction(self):
        """Todos los campos presentes → modelo válido."""
        item = TimelineItem(
            id="cccccccc-cccc-cccc-cccc-cccccccccccc",
            date="2019-03-15",
            title="Diagnóstico HTA",
            description="Primera consulta.",
            is_critical=True,
        )
        assert item.is_critical is True
        assert item.date == "2019-03-15"

    def test_empty_date_allowed(self):
        """date puede ser cadena vacía."""
        item = TimelineItem(
            id="cccccccc-cccc-cccc-cccc-cccccccccccc",
            date="",
            title="Evento sin fecha",
            description="Sin fecha.",
            is_critical=False,
        )
        assert item.date == ""

    def test_missing_required_field(self):
        """Omitir 'is_critical' → ValidationError."""
        with pytest.raises(ValidationError):
            TimelineItem(  # type: ignore[call-arg]
                id="cccccccc-cccc-cccc-cccc-cccccccccccc",
                date="2020-01-01",
                title="Evento",
                description="Desc.",
            )


# ---------------------------------------------------------------------------
# SummaryResponse
# ---------------------------------------------------------------------------


class TestSummaryResponse:
    def _make_domain(self) -> DomainItem:
        return DomainItem(
            id="aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
            title="Cardiología",
            status="ok",
            description="Estable.",
        )

    def _make_alert(self) -> AlertItem:
        return AlertItem(
            id="bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb",
            title="Alerta",
            status="warn",
            description="Desc.",
        )

    def _make_timeline_item(self) -> TimelineItem:
        return TimelineItem(
            id="cccccccc-cccc-cccc-cccc-cccccccccccc",
            date="2020-01-01",
            title="Evento",
            description="Desc.",
            is_critical=False,
        )

    def test_full_response(self):
        """Construir con todos los campos → válido."""
        resp = SummaryResponse(
            patient_id="11111111-1111-1111-1111-111111111111",
            domains=[self._make_domain()],
            alerts=[self._make_alert()],
            timeline=[self._make_timeline_item()],
        )
        assert resp.patient_id == "11111111-1111-1111-1111-111111111111"
        assert len(resp.domains) == 1
        assert len(resp.alerts) == 1
        assert len(resp.timeline) == 1

    def test_empty_arrays(self):
        """Arrays vacíos → válido."""
        resp = SummaryResponse(
            patient_id="11111111-1111-1111-1111-111111111111",
            domains=[],
            alerts=[],
            timeline=[],
        )
        assert resp.domains == []
        assert resp.alerts == []
        assert resp.timeline == []

    def test_missing_patient_id(self):
        """Sin patient_id → ValidationError."""
        with pytest.raises(ValidationError):
            SummaryResponse(  # type: ignore[call-arg]
                domains=[],
                alerts=[],
                timeline=[],
            )
