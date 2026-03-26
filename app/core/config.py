from functools import lru_cache
from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # LLM Provider
    OPENAI_API_KEY: SecretStr = SecretStr("")
    MODEL_NAME: str = "gpt-4o"
    LLM_PROVIDER: str = "openai"

    # Application
    APP_ENV: str = "development"
    LOG_LEVEL: str = "INFO"
    MAX_HISTORIA_CHARS: int = 50_000

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
