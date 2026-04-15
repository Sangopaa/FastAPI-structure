import os
import pytest
import asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel

# Ensure all models are registered in SQLModel.metadata before create_all
import models
from configurations.database import get_session
from main import app


# ---------------------------------------------------------------------------
# Asynchronous Database Fixtures
#
# Configures the test environment for a 100% asynchronous flow using
# SQLAlchemy AsyncIO and the asyncpg driver.
#
# NOTE ON SCHEMAS:
# AutoTableMeta assigns PostgreSQL schemas based on model paths (e.g., `accounts`).
# Because schemas are a PostgreSQL-specific feature, SQLite is NOT supported.
#
# Test Session Lifecycle:
#   1. Event Loop: Initializes a session-scoped asyncio event loop.
#   2. Engine: Creates an `AsyncEngine` using the `+asyncpg` dialect.
#   3. Schemas: Asynchronously ensures all unique schemas exist in the DB.
#   4. Tables: Maps `SQLModel.metadata.create_all` via `conn.run_sync` to
#      bridge synchronous metadata definition with the async connection.
#   5. Injection: Overrides `get_session` to provide an `AsyncSession`
#      with automatic rollback per test to ensure isolation.
#   6. Cleanup: Drops all tables and disposes of the engine at teardown.
# ---------------------------------------------------------------------------


@pytest.fixture(name="engine", scope="session")
async def engine_fixture():
    connection_string = os.environ.get("CONNECTION_STRING")
    if not connection_string:
        raise RuntimeError("CONNECTION_STRING is not set in .env.test")

    # Usar el motor asíncrono
    engine = create_async_engine(connection_string, pool_pre_ping=True)

    # Crear esquemas y tablas
    async with engine.begin() as conn:
        # Extraer esquemas únicos de los modelos
        schemas = set(t.schema for t in SQLModel.metadata.tables.values() if t.schema)
        for schema in schemas:
            await conn.execute(text(f'CREATE SCHEMA IF NOT EXISTS "{schema}"'))

        # SQLModel.metadata.create_all necesita ejecutarse vía run_sync
        await conn.run_sync(SQLModel.metadata.create_all)

    yield engine

    # Limpieza al terminar los tests
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)
    await engine.dispose()


@pytest.fixture(name="session")
async def session_fixture(engine):
    """Proporciona una AsyncSession limpia por test."""
    async_session_maker = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    async with async_session_maker() as session:
        yield session
        # Rollback automático para que un test no ensucie al siguiente
        await session.rollback()


@pytest.fixture(name="client")
async def client_fixture(session: AsyncSession):
    """
    Inyecta la sesión de test asíncrona en la app.
    """

    # Sobrescribimos la dependencia original
    async def override_get_session():
        yield session

    app.dependency_overrides[get_session] = override_get_session

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac

    app.dependency_overrides.clear()
