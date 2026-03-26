"""
Configuración global de tests para backend_clinic_copilot_nlp.
"""

import pytest
from fastapi.testclient import TestClient

from app.infrastructure.llm.base import LLMProvider, LLMResponse

# ---------------------------------------------------------------------------
# FakeLLMProvider — responde con JSON válido sin llamar a ninguna API real
# ---------------------------------------------------------------------------

FAKE_JSON_RESPONSE = """{
  "domains": [
    {"title": "Cardiología - HTA", "status": "warn", "description": "HTA estadio 2 con IRC estadio 3."},
    {"title": "Nefrología - IRC estadio 3", "status": "warn", "description": "Creatinina 2.8 mg/dL."}
  ],
  "alerts": [
    {"title": "Uso de AINEs contraindicado", "status": "danger", "description": "IRC reduce clearance renal. AINEs contraindicados."}
  ],
  "timeline": [
    {"date": "2018-01-01", "title": "Diagnóstico HTA + IRC", "description": "Primera consulta. Inicio de enalapril.", "is_critical": true}
  ]
}"""


class FakeLLMProvider(LLMProvider):
    """Proveedor LLM falso para tests — nunca llama a APIs externas."""

    @property
    def provider_name(self) -> str:
        return "fake"

    async def generate(self, system_prompt: str, user_prompt: str) -> LLMResponse:
        return LLMResponse(
            content=FAKE_JSON_RESPONSE,
            tokens_input=100,
            tokens_output=50,
            model="fake-model",
            provider="fake",
        )


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(autouse=True)
def clear_settings_cache(monkeypatch):
    """
    Limpia el caché de get_settings antes y después de cada test,
    e inyecta variables de entorno seguras para tests.
    """
    from app.core.config import get_settings

    get_settings.cache_clear()
    monkeypatch.setenv("OPENAI_API_KEY", "sk-fake-key-for-tests")
    monkeypatch.setenv("MODEL_NAME", "gpt-4o")
    monkeypatch.setenv("LLM_PROVIDER", "openai")
    monkeypatch.setenv("APP_ENV", "test")
    monkeypatch.setenv("LOG_LEVEL", "WARNING")
    monkeypatch.setenv("DATABASE_URL", "postgresql+asyncpg://fake:fake@localhost/fake")
    yield
    get_settings.cache_clear()


@pytest.fixture
def fake_provider() -> FakeLLMProvider:
    """Instancia del FakeLLMProvider para usar en unit tests."""
    return FakeLLMProvider()


@pytest.fixture
def client():
    """
    TestClient con FakeLLMProvider inyectado en app.state.

    IMPORTANTE: el lifespan de FastAPI se ejecuta al entrar en el bloque `with`.
    init_db() se mockea para que no intente conectarse a la base de datos real
    durante los tests. El proveedor LLM también se sobrescribe con el fake.
    """
    from unittest.mock import AsyncMock, patch

    from app.main import app

    with (
        patch("app.main.init_db", new=AsyncMock()),
        TestClient(app, raise_server_exceptions=False) as c,
    ):
        # El lifespan ya corrió; ahora sobreescribimos el proveedor con el fake
        app.state.llm_provider = FakeLLMProvider()
        yield c


@pytest.fixture
def valid_historia() -> str:
    """Historia clínica realista de 200+ caracteres para tests de integración."""
    return (
        "Paciente masculino de 58 años con antecedentes de hipertensión arterial e "
        "insuficiencia renal crónica estadio 3. Diagnóstico inicial en 2018. "
        "Tratamiento actual con enalapril 10mg cada 12 horas y amlodipina 5mg diarios. "
        "Última consulta evidencia deterioro de función renal con creatinina 2.8 mg/dL."
    )
