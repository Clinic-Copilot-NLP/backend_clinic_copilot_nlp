import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.routes import analyze, clinical, health, patients
from app.core.config import get_settings
from app.db.base import engine, init_db
from app.infrastructure.llm.base import LLMProviderError
from app.infrastructure.llm.factory import get_llm_provider
from app.api.routes import auth

logging.basicConfig(level="INFO")
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    logger.info("Starting Clinical Copilot NLP API")
    logger.info(f"Provider: {settings.LLM_PROVIDER} | Model: {settings.MODEL_NAME}")

    await init_db()

    provider = get_llm_provider(settings)
    app.state.llm_provider = provider
    logger.info(f"LLM provider ready: {provider.provider_name}")

    yield

    logger.info("Shutting down Clinical Copilot NLP API")
    await engine.dispose()


app = FastAPI(
    title="Clinical Copilot NLP",
    description="Summarizes patient clinical histories using LLMs",
    version="0.1.0",
    lifespan=lifespan,
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(LLMProviderError)
async def llm_provider_error_handler(request: Request, exc: LLMProviderError) -> JSONResponse:
    logger.error(f"LLM provider error: {exc}")
    return JSONResponse(
        status_code=503,
        content={"detail": str(exc), "provider": exc.provider},
    )


app.include_router(health.router, tags=["health"])
app.include_router(patients.router, prefix="/api/v1", tags=["patients"])
app.include_router(analyze.router, prefix="/api/v1", tags=["analyze"])
app.include_router(clinical.router, prefix="/api/v1", tags=["clinical"])
app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
