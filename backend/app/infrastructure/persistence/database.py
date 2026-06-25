"""Database initialization and management."""

import logging
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

# Async engine and session factory - will be initialized in ServiceRegistry
_engine = None
_session_factory = None


async def initialize_database() -> None:
    """Initialize database connection and create engine.
    
    This is called during application startup.
    """
    global _engine, _session_factory
    
    logger.info(f"Initializing PostgreSQL connection: {settings.database_url[:50]}...")
    
    _engine = create_async_engine(
        settings.database_url,
        echo=settings.debug,
        pool_size=settings.database_pool_size,
        max_overflow=settings.database_max_overflow,
        pool_timeout=settings.database_pool_timeout,
        pool_recycle=settings.database_pool_recycle,
    )
    
    _session_factory = async_sessionmaker(
        _engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,
    )
    
    logger.info("Database initialized successfully")


async def cleanup_database() -> None:
    """Clean up database connections.
    
    This is called during application shutdown.
    """
    global _engine
    
    if _engine:
        logger.info("Closing database connections...")
        await _engine.dispose()
        logger.info("Database connections closed")


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Get database session for dependency injection.
    
    Yields:
        AsyncSession instance.
        
    Raises:
        RuntimeError: If database not initialized.
    """
    if not _session_factory:
        raise RuntimeError("Database not initialized. Call initialize_database() first.")
    
    async with _session_factory() as session:
        try:
            yield session
        finally:
            await session.close()


def get_session_factory():
    """Get session factory.
    
    Returns:
        AsyncSessionMaker instance.
        
    Raises:
        RuntimeError: If database not initialized.
    """
    if not _session_factory:
        raise RuntimeError("Database not initialized. Call initialize_database() first.")
    return _session_factory
