import os

import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy import text
from sqlmodel import SQLModel, Session, create_engine

# Ensure all models are registered in SQLModel.metadata before create_all
import models  # noqa: F401

from configurations.database import get_session
from main import app


# ---------------------------------------------------------------------------
# Database fixtures
#
# Uses the PostgreSQL test container (CONNECTION_STRING from .env.test).
# AutoTableMeta assigns schemas based on the model module path (e.g. `accounts`),
# so SQLite cannot be used — schemas are a PostgreSQL-only feature.
#
# Flow per test session:
#   1. Connect to db_test (PostgreSQL container)
#   2. Create all required schemas
#   3. Create all tables via SQLModel.metadata.create_all
#   4. Yield engine
#   5. Drop all tables at teardown
# ---------------------------------------------------------------------------


def _get_schemas_from_metadata() -> set[str]:
    """Collect all unique schema names declared across registered models."""
    schemas = set()
    for table in SQLModel.metadata.tables.values():
        if table.schema:
            schemas.add(table.schema)
    return schemas


@pytest.fixture(name="engine", scope="session")
def engine_fixture():
    """
    Creates a PostgreSQL engine pointing to the isolated test database.
    Creates required schemas and all tables before yielding.
    """
    connection_string = os.environ.get("CONNECTION_STRING")
    if not connection_string:
        raise RuntimeError(
            "CONNECTION_STRING is not set. "
            "Make sure .env.test is loaded (via docker-compose.test.yml or locally)."
        )

    engine = create_engine(connection_string, pool_pre_ping=True)

    with engine.connect() as conn:
        for schema in _get_schemas_from_metadata():
            conn.execute(text(f"CREATE SCHEMA IF NOT EXISTS {schema}"))
        conn.commit()

    SQLModel.metadata.create_all(engine)
    yield engine
    SQLModel.metadata.drop_all(engine)


@pytest.fixture(name="session")
def session_fixture(engine):
    """
    Provides a clean Session per test with automatic rollback.
    """
    with Session(engine) as session:
        yield session
        session.rollback()


@pytest.fixture(name="client")
async def client_fixture(session: Session):
    """
    Provides an async HTTP test client with the real FastAPI app.
    Overrides `get_session` to inject the isolated test session.
    """

    def override_get_session():
        yield session

    app.dependency_overrides[get_session] = override_get_session

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac

    app.dependency_overrides.clear()
