import logging
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from src.config import settings
from src.database.models import Base

logger = logging.getLogger("lenny_assistant.database")

# Create engine
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,
    future=True
)

async_session_factory = async_sessionmaker(
    engine, 
    expire_on_commit=False, 
    class_=AsyncSession
)

async def init_db() -> None:
    """Initialize database tables."""
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info(f"Database initialized successfully at: {settings.DATABASE_URL}")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise

async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Dependency for providing an async database session."""
    async with async_session_factory() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
