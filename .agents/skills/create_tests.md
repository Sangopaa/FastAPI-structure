# Skill: Creating New Tests

This guide explains the standard procedure for writing automated tests in our async FastAPI project using Pytest.

## 1. Location of Tests
All test files must reside within the `tests/` directory.
- Name test files with a `test_` prefix (e.g., `test_users.py`, `test_services.py`).
- Maintain a directory structure in `tests/` that mirrors the application structure if possible.

## 2. Using Pytest-Asyncio
Since the application uses `AsyncSession` and asynchronous definitions for endpoints, services, and repositories, tests must also run asynchronously.
- Use the `@pytest.mark.asyncio` decorator on your async test cases.
- Use `httpx.AsyncClient` for testing API endpoints instead of the standard synchronous `TestClient`.

## 3. Writing Endpoint Tests
Testing the API layer requires sending HTTP requests and asserting the response codes and payloads.

```python
import pytest
from httpx import AsyncClient, ASGITransport
from main import app # replace with your actual app import

@pytest.mark.asyncio
async def test_create_entity():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post("/api/v1/my-entities/", json={"name": "Test Name", "special_field": "123"})

    assert response.status_code == 201
    assert response.json()["data"]["name"] == "Test Name"

@pytest.mark.asyncio
async def test_get_entities():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/api/v1/my-entities/")

    assert response.status_code == 200
    # Pagination structure assertions
    assert "data" in response.json()
    assert isinstance(response.json()["data"], list)
```

## 4. Writing Service and Repository Tests
When testing services or repositories directly, you must provide a database `AsyncSession`. A test session fixture should be available in your `conftest.py`.

```python
import pytest
from repositories.my_entity import my_entity_repository
from schemas.my_entity import MyEntityCreate

@pytest.mark.asyncio
async def test_repository_create(db_session):
    # db_session is injected via pytest fixtures
    new_entity_data = MyEntityCreate(name="Repo Test", special_field="abc")

    # Needs a real or mocked entity to be created
    from models.my_entity import MyEntity
    entity = MyEntity(**new_entity_data.model_dump())

    created = await my_entity_repository.create(db_session, entity)

    assert created.id is not None
    assert created.name == "Repo Test"
```

## 5. Mocking Dependencies
If you need to test routers without hitting the real database, consider overriding the `get_session` dependency using `app.dependency_overrides`.

```python
from configurations.database import get_session

async def override_get_session():
    # Return a mocked session or a special test DB session
    yield test_session

app.dependency_overrides[get_session] = override_get_session
```

## Summary
- Use `@pytest.mark.asyncio` for test functions.
- Use `httpx.AsyncClient` for endpoint HTTP requests.
- Utilize your `db_session` fixture to test services and repositories directly.
- Clear out the test database before or after test runs as configured in your `conftest.py`.
