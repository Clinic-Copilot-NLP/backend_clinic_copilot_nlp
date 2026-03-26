from functools import lru_cache

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # LLM Provider
    OPENAI_API_KEY: SecretStr = Field()
    MODEL_NAME: str = Field()
    LLM_PROVIDER: str = Field()

    # Application
    APP_ENV: str = Field()
    LOG_LEVEL: str = Field()
    MAX_HISTORIA_CHARS: int = 50_000

    # Database
    DATABASE_URL: str = Field()

    # Auth
    SECRET_KEY: str = Field()
    TOKEN_EXPIRE_HOURS: int = Field(default=12)
    DOCTOR_ID: str = Field(default="1")
    DOCTOR_EMAIL: str = Field()
    DOCTOR_PASSWORD: str = Field()
    DOCTOR_NAME: str = Field()
    DOCTOR_SPECIALTY: str = Field()
    DOCTOR_AVATAR_INITIALS: str = Field(default="")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()  # type: ignore
