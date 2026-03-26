import logging
import secrets

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.api.schemas.auth import LoginRequest, LoginResponse, UserOut
from app.core.config import get_settings
from app.core.security import create_access_token, decode_access_token

logger = logging.getLogger(__name__)

router = APIRouter()
_bearer = HTTPBearer()


def _get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(_bearer),
) -> UserOut:
    """Dependencia que extrae y verifica el token Bearer, retorna el médico autenticado."""
    payload = decode_access_token(credentials.credentials)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )
    settings = get_settings()
    return UserOut(
        id=settings.DOCTOR_ID,
        name=settings.DOCTOR_NAME,
        email=settings.DOCTOR_EMAIL,
        specialty=settings.DOCTOR_SPECIALTY,
        avatar_initials=settings.DOCTOR_AVATAR_INITIALS,
    )


@router.post("/login", response_model=LoginResponse)
async def login(body: LoginRequest) -> LoginResponse:
    """
    Autentica al médico con email y contraseña.
    Retorna un token JWT y los datos del usuario.
    """
    settings = get_settings()

    # Comparación en tiempo constante para evitar timing attacks
    email_ok = secrets.compare_digest(body.email.lower(), settings.DOCTOR_EMAIL.lower())
    password_ok = secrets.compare_digest(body.password, settings.DOCTOR_PASSWORD)

    if not email_ok or not password_ok:
        logger.warning(f"Intento de login fallido | email={body.email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales inválidas",
        )

    user = UserOut(
        id=settings.DOCTOR_ID,
        name=settings.DOCTOR_NAME,
        email=settings.DOCTOR_EMAIL,
        specialty=settings.DOCTOR_SPECIALTY,
        avatar_initials=settings.DOCTOR_AVATAR_INITIALS,
    )
    token = create_access_token({"sub": user.id, "email": user.email})
    logger.info(f"Login exitoso | email={user.email}")
    return LoginResponse(access_token=token, token_type="bearer", user=user)


@router.get("/me", response_model=UserOut)
async def get_me(current_user: UserOut = Depends(_get_current_user)) -> UserOut:
    """Retorna los datos del médico autenticado a partir del token Bearer."""
    return current_user


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout() -> None:
    """
    Cierre de sesión.
    El token JWT es stateless — el cliente debe eliminarlo localmente.
    """
    return None
