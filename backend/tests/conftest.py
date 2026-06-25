"""Pytest configuration and fixtures."""

import asyncio
import os

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import Settings
from app.main import create_app


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def test_settings() -> Settings:
    """Create test settings."""
    return Settings(
        app_env="testing",
        debug=True,
        database_url="sqlite+aiosqlite:///:memory:",
    )


@pytest.fixture
async def app():
    """Create FastAPI test application."""
    return create_app()


@pytest.fixture
async def client(app):
    """Create async HTTP client for testing."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


@pytest.fixture
async def test_db_engine():
    """Create in-memory test database engine."""
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        echo=False,
    )
    
    async with engine.begin() as conn:
        # Create tables here if needed
        pass
    
    yield engine
    
    await engine.dispose()


@pytest.fixture
async def test_session(test_db_engine):
    """Create test database session."""
    async_session = sessionmaker(
        test_db_engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session() as session:
        yield session
