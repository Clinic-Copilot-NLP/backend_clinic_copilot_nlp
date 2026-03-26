import logging
from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.core.config import get_settings

logger = logging.getLogger(__name__)


class Base(DeclarativeBase):
    pass


def _create_engine() -> object:
    settings = get_settings()
    logger.info("Creating async database engine")
    return create_async_engine(
        settings.DATABASE_URL,
        echo=False,
        pool_pre_ping=True,
    )


engine = _create_engine()

AsyncSessionLocal: async_sessionmaker[AsyncSession] = async_sessionmaker(
    bind=engine,  # type: ignore[arg-type]
    class_=AsyncSession,
    expire_on_commit=False,
)


async def init_db() -> None:
    """Crea todas las tablas definidas en los modelos si no existen."""
    # Importar modelos para que SQLAlchemy los registre en Base.metadata
    import app.db.models.clinical_analysis  # noqa: F401
    import app.db.models.patient  # noqa: F401

    async with engine.begin() as conn:  # type: ignore[union-attr]
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables created (create_all)")


async def get_db() -> AsyncGenerator[AsyncSession]:
    """Generador de sesión de base de datos para FastAPI Depends."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
