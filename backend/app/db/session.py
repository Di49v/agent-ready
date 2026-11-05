"""
Database Session and Engine Management for AgentReady Lab.
Configured for Supabase PostgreSQL using asyncpg with connection pooling
and statement_cache_size=0 for Supabase transaction pooler compatibility.
"""
from typing import AsyncIterator, Optional
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from app.core.config import get_settings


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy Declarative Models."""
    pass


_engine: Optional[AsyncEngine] = None
_session_maker: Optional[async_sessionmaker[AsyncSession]] = None


def get_db_url() -> str:
    """
    Normalizes database connection string to ensure asyncpg dialect.
    Handles 'postgres://' and 'postgresql://' prefixes from Supabase/Render.
    """
    settings = get_settings()
    url = settings.DATABASE_URL
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql+asyncpg://", 1)
    elif url.startswith("postgresql://"):
        url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
    return url


def get_engine() -> AsyncEngine:
    """Returns or creates the singleton async SQLAlchemy engine."""
    global _engine
    if _engine is None:
        db_url = get_db_url()
        connect_args = {}

        # Supabase transaction poolers (PgBouncer) require disabling prepared statement cache
        if "postgresql" in db_url or "asyncpg" in db_url:
            connect_args["statement_cache_size"] = 0

        _engine = create_async_engine(
            db_url,
            echo=False,
            future=True,
            pool_pre_ping=True,
            connect_args=connect_args,
        )
    return _engine


def get_session_maker() -> async_sessionmaker[AsyncSession]:
    """Returns the configured async sessionmaker."""
    global _session_maker
    if _session_maker is None:
        _session_maker = async_sessionmaker(
            bind=get_engine(),
            class_=AsyncSession,
            expire_on_commit=False,
            autocommit=False,
            autoflush=False,
        )
    return _session_maker


async def get_db() -> AsyncIterator[AsyncSession]:
    """FastAPI dependency yielding an async database session."""
    session_factory = get_session_maker()
    async with session_factory() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db() -> None:
    """Initializes all database tables defined on Base metadata."""
    engine = get_engine()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

