from fastapi import APIRouter, Request

from app.core.config import get_settings

router = APIRouter()


@router.get("/health")
async def health_check(request: Request) -> dict:
    settings = get_settings()
    return {
        "status": "ok",
        "provider": settings.LLM_PROVIDER,
        "model": settings.MODEL_NAME,
        "env": settings.APP_ENV,
    }
