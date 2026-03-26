"""
Módulo de seguridad: generación y verificación de tokens JWT para autenticación de médicos.
"""
import logging
from datetime import datetime, timedelta, timezone

import jwt

from app.core.config import get_settings

logger = logging.getLogger(__name__)

_ALGORITHM = "HS256"


def create_access_token(data: dict) -> str:
    """Genera un token JWT firmado con los datos del médico y tiempo de expiración."""
    settings = get_settings()
    payload = data.copy()
    payload["exp"] = datetime.now(timezone.utc) + timedelta(hours=settings.TOKEN_EXPIRE_HOURS)
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=_ALGORITHM)


def decode_access_token(token: str) -> dict | None:
    """
    Verifica y decodifica un token JWT.
    Retorna el payload si es válido, None si expiró o es inválido.
    """
    settings = get_settings()
    try:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=[_ALGORITHM])
    except jwt.ExpiredSignatureError:
        logger.warning("Token JWT expirado.")
        return None
    except jwt.PyJWTError as e:
        logger.warning(f"Token JWT inválido: {e}")
        return None
