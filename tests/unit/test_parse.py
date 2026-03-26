"""
Tests de parseo por sección para _parse_clinical_response.

Verifica el comportamiento de fallback independiente por sección:
- JSON completo inválido → arrays vacíos para las 3 secciones
- Sección de arreglo malformada → esa sección = [], otras secciones OK
- JSON completo válido → todos los datos presentes
"""

import json

from app.core.services.summarizer import _parse_clinical_response

# ---------------------------------------------------------------------------
# Constantes de prueba
# ---------------------------------------------------------------------------

VALID_FULL_JSON = json.dumps(
    {
        "domains": [
            {"title": "Cardiología - HTA", "status": "warn", "description": "HTA estadio 2."}
        ],
        "alerts": [{"title": "HbA1c elevada", "status": "warn", "description": "Ajuste requerido"}],
        "timeline": [
            {
                "date": "2018-05-10",
                "title": "Diagnóstico HTA",
                "description": "Primera consulta.",
                "is_critical": False,
            }
        ],
    }
)


# ---------------------------------------------------------------------------
# Fallback completo: respuesta no-JSON
# ---------------------------------------------------------------------------


class TestFullJsonParseFailure:
    def test_garbage_input_array_fields_empty(self):
        """Entrada no-JSON → todos los campos de arreglo son []."""
        result = _parse_clinical_response("esto no es JSON de ninguna manera")
        assert result["domains"] == []
        assert result["alerts"] == []
        assert result["timeline"] == []

    def test_garbage_input_returns_all_3_keys(self):
        """Entrada no-JSON → resultado siempre tiene las 3 claves."""
        result = _parse_clinical_response("garbage")
        expected_keys = {"domains", "alerts", "timeline"}
        assert set(result.keys()) == expected_keys

    def test_empty_string_input(self):
        """Cadena vacía → no lanza excepción, retorna todas las claves."""
        result = _parse_clinical_response("")
        assert isinstance(result, dict)
        assert "domains" in result
        assert "alerts" in result
        assert "timeline" in result

    def test_whitespace_only_input(self):
        """Solo espacios en blanco → no lanza excepción."""
        result = _parse_clinical_response("   ")
        assert isinstance(result, dict)
        assert result["domains"] == []
        assert result["alerts"] == []
        assert result["timeline"] == []


# ---------------------------------------------------------------------------
# Fallback parcial: un array malformado en JSON válido
# ---------------------------------------------------------------------------


class TestPartialArrayFailure:
    def _make_json_with_bad_alerts(self) -> dict:
        return {
            "domains": [{"title": "Cardiología", "status": "ok", "description": "Estable."}],
            "alerts": "ESTO_NO_ES_ARRAY",
            "timeline": [
                {
                    "date": "2020-01-01",
                    "title": "Control",
                    "description": "Rutina.",
                    "is_critical": False,
                }
            ],
        }

    def test_non_list_array_field_defaults_to_empty(self):
        """alerts con string en vez de lista → alerts = []."""
        result = _parse_clinical_response(json.dumps(self._make_json_with_bad_alerts()))
        assert result["alerts"] == []

    def test_other_array_fields_preserved(self):
        """alerts inválida → domains y timeline se preservan."""
        result = _parse_clinical_response(json.dumps(self._make_json_with_bad_alerts()))
        assert len(result["domains"]) == 1
        assert len(result["timeline"]) == 1

    def test_domains_preserved_on_alerts_failure(self):
        """alerts inválida → domains se preserva correctamente."""
        result = _parse_clinical_response(json.dumps(self._make_json_with_bad_alerts()))
        assert result["domains"][0]["title"] == "Cardiología"
        assert result["domains"][0]["status"] == "ok"


# ---------------------------------------------------------------------------
# Happy path: JSON completo y válido
# ---------------------------------------------------------------------------


class TestValidFullJsonParse:
    def test_valid_json_all_array_fields_populated(self):
        """JSON completo → todos los campos de arreglo correctamente parseados."""
        result = _parse_clinical_response(VALID_FULL_JSON)
        assert len(result["domains"]) == 1
        assert len(result["alerts"]) == 1
        assert len(result["timeline"]) == 1

    def test_valid_json_domains_content(self):
        """domains contiene el dict correcto."""
        result = _parse_clinical_response(VALID_FULL_JSON)
        assert result["domains"][0]["title"] == "Cardiología - HTA"
        assert result["domains"][0]["status"] == "warn"

    def test_valid_json_alerts_content(self):
        """alerts contiene el dict correcto."""
        result = _parse_clinical_response(VALID_FULL_JSON)
        assert result["alerts"][0]["title"] == "HbA1c elevada"
        assert result["alerts"][0]["status"] == "warn"

    def test_valid_json_timeline_content(self):
        """timeline contiene el dict correcto."""
        result = _parse_clinical_response(VALID_FULL_JSON)
        assert result["timeline"][0]["title"] == "Diagnóstico HTA"
        assert result["timeline"][0]["is_critical"] is False

    def test_markdown_fenced_json_parsed_correctly(self):
        """JSON dentro de bloque ```json...``` → mismo resultado que JSON plano."""
        fenced = f"```json\n{VALID_FULL_JSON}\n```"
        result = _parse_clinical_response(fenced)
        assert result["domains"][0]["title"] == "Cardiología - HTA"
        assert len(result["alerts"]) == 1

    def test_missing_array_field_defaults_to_empty(self):
        """JSON válido sin campo 'alerts' → alerts = []."""
        data = {
            "domains": [{"title": "Cardiología", "status": "ok", "description": "Estable."}],
            "timeline": [],
        }
        result = _parse_clinical_response(json.dumps(data))
        assert result["alerts"] == []

    def test_returns_dict_with_all_3_keys(self):
        """El resultado siempre contiene las 3 claves esperadas."""
        result = _parse_clinical_response("garbage input")
        expected_keys = {"domains", "alerts", "timeline"}
        assert expected_keys == set(result.keys())


# ---------------------------------------------------------------------------
# Contrato de IDs: _parse_clinical_response NO inyecta IDs (lo hace analyze)
# ---------------------------------------------------------------------------


class TestParseDoesNotInjectIds:
    def test_parsed_items_do_not_have_id_field(self):
        """_parse_clinical_response no inyecta 'id' — lo hace analyze() antes de persistir."""
        result = _parse_clinical_response(VALID_FULL_JSON)
        for key in ("domains", "alerts", "timeline"):
            for item in result[key]:
                assert "id" not in item, (
                    f"_parse_clinical_response no debe inyectar 'id' en '{key}' items"
                )

    def test_parsed_items_preserve_id_if_llm_provides_one(self):
        """Si el LLM incluyera 'id' en la respuesta, se preserva sin modificar."""
        import json

        data_with_id = {
            "domains": [
                {"id": "llm-provided-id", "title": "T", "status": "ok", "description": "D"}
            ],
            "alerts": [],
            "timeline": [],
        }
        result = _parse_clinical_response(json.dumps(data_with_id))
        assert result["domains"][0]["id"] == "llm-provided-id"
