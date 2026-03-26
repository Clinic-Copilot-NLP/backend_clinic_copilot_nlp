"""
Tests unitarios para la configuración de la aplicación (Settings / get_settings).
"""

from pydantic import SecretStr

from app.core.config import get_settings


class TestSettings:
    def test_settings_loaded_from_env(self, monkeypatch):
        """get_settings() carga correctamente los valores desde el entorno."""
        monkeypatch.setenv("LLM_PROVIDER", "openai")
        monkeypatch.setenv("MODEL_NAME", "gpt-4o")
        monkeypatch.setenv("APP_ENV", "test")
        monkeypatch.setenv("LOG_LEVEL", "WARNING")
        get_settings.cache_clear()

        settings = get_settings()
        assert settings.LLM_PROVIDER == "openai"
        assert settings.MODEL_NAME == "gpt-4o"
        assert settings.APP_ENV == "test"
        assert settings.LOG_LEVEL == "WARNING"

    def test_settings_lru_cache(self):
        """Llamar get_settings() dos veces retorna el mismo objeto (is check)."""
        s1 = get_settings()
        s2 = get_settings()
        assert s1 is s2

    def test_settings_cache_clear_refreshes(self, monkeypatch):
        """Limpiar caché + cambiar env → get_settings() refleja el cambio."""
        monkeypatch.setenv("APP_ENV", "production")
        get_settings.cache_clear()

        settings = get_settings()
        assert settings.APP_ENV == "production"

    def test_openai_api_key_is_secret_str(self):
        """OPENAI_API_KEY debe ser SecretStr, nunca un str plano."""
        settings = get_settings()
        assert isinstance(settings.OPENAI_API_KEY, SecretStr)

    def test_max_historia_chars_default(self):
        """MAX_HISTORIA_CHARS debe ser 50.000 por defecto."""
        settings = get_settings()
        assert settings.MAX_HISTORIA_CHARS == 50_000
