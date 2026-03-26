from contextlib import asynccontextmanager
import logging
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.core.config import get_settings
from app.infrastructure.llm.factory import get_llm_provider
from app.infrastructure.llm.base import LLMProviderError
from app.api.routes import health, analyze

logging.basicConfig(level="INFO")
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    logger.info("Starting Clinical Copilot NLP API")
    logger.info(f"Provider: {settings.LLM_PROVIDER} | Model: {settings.MODEL_NAME}")

    provider = get_llm_provider(settings)
    app.state.llm_provider = provider
    logger.info(f"LLM provider ready: {provider.provider_name}")

    yield

    logger.info("Shutting down Clinical Copilot NLP API")


app = FastAPI(
    title="Clinical Copilot NLP",
    description="Summarizes patient clinical histories using LLMs",
    version="0.1.0",
    lifespan=lifespan,
)


@app.exception_handler(LLMProviderError)
async def llm_provider_error_handler(
    request: Request, exc: LLMProviderError
) -> JSONResponse:
    logger.error(f"LLM provider error: {exc}")
    return JSONResponse(
        status_code=503,
        content={"detail": str(exc), "provider": exc.provider},
    )


app.include_router(health.router, tags=["health"])
app.include_router(analyze.router, prefix="/api", tags=["analyze"])
