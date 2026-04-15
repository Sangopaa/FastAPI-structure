# Skill: Creating New Endpoints in FastAPI

This guide explains the standard procedure and best practices for creating new endpoints in this FastAPI project. The project follows a strict layered architecture pattern: Router (API) -> Service -> Repository. Note that the project utilizes asynchronous database operations.

## 1. Domain Models and Schemas
Before creating endpoints, ensure your database models and Pydantic schemas are defined.
- **Database Models**: Place in `models/`. Use `sqlmodel.SQLModel`.
- **Schemas**: Place in `schemas/`. Use these for Request payloads and Response formatting (e.g., `MyEntityCreate`, `MyEntityResponse`).

## 2. Repository Layer (Database Access)
All database interactions should be encapsulated within the `repositories/` directory.

- Create a new file in `repositories/` (e.g., `repositories/my_entity.py`).
- Inherit from `BaseRepository` (found in `repositories/base.py`).
- The repository class should take the SQLAlchemy/SQLModel class.
- Use `AsyncSession` and `await` for all database operations.
- Create a global singleton instance of the repository at the bottom of the file.

```python
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from models.my_entity import MyEntity
from .base import BaseRepository

class MyEntityRepository(BaseRepository[MyEntity]):
    def __init__(self):
        super().__init__(MyEntity)

    # Add custom database queries here if the base ones are not enough
    async def get_by_special_field(self, session: AsyncSession, field_value: str):
        statement = select(self.model).where(self.model.special_field == field_value)
        result = await session.execute(statement)
        return result.scalars().first()

# Singleton instance
my_entity_repository = MyEntityRepository()
```

## 3. Service Layer (Business Logic)
Keep business logic out of the routers. The service layer handles validation, coordinating repositories, and throwing HTTPExceptions.

- Create a new file in `services/` (e.g., `services/my_entity.py`).
- Create a service class and instantiate it at the end of the file.
- Services should depend on the repository instance.
- Pass the database `AsyncSession` from the router to the service methods.
- Define methods as `async def`.
- Raise `fastapi.HTTPException` here for business logic faults (e.g., item not found, validation error).

```python
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from models.my_entity import MyEntity
from schemas.my_entity import MyEntityCreate
from repositories.my_entity import my_entity_repository

class MyEntityService:
    def __init__(self):
        self.repository = my_entity_repository

    async def create_entity(self, session: AsyncSession, data: MyEntityCreate) -> MyEntity:
        # Business logic validation
        existing_entity = await self.repository.get_by_special_field(session, data.special_field)
        if existing_entity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Entity already exists"
            )

        entity = MyEntity(**data.model_dump())
        return await self.repository.create(session, entity)

# Singleton instance
my_entity_service = MyEntityService()
```

## 4. API Layer (Routers)
The endpoints should only handle HTTP concerns: extracting dependencies, calling the service layer, and returning responses.

- Create a router file in `api/v1/endpoints/` (e.g., `api/v1/endpoints/my_entities.py`).
- Use `GenericCRUDRouter` or standard `APIRouter` if generic endpoints do not apply.
- Use dependency injection for the asynchronous database session.

```python
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from configurations.database import get_session
from schemas.my_entity import MyEntityCreate, MyEntityResponse
from services.my_entity import my_entity_service

router = APIRouter()

@router.post("/", summary="Create an Entity", response_model=MyEntityResponse)
async def create_entity(
    data: MyEntityCreate,
    session: AsyncSession = Depends(get_session)
):
    entity = await my_entity_service.create_entity(session, data)
    return {"message": "Success", "data": entity}
```

## 5. Register the Router
Finally, you must include your new router in the main routing file so the app can discover it.

- Open `api/v1/api_router.py`.
- Import your new router module.
- Add it to `v1_router` using `include_router`. Provide an appropriate `prefix` and `tags`.

```python
from api.v1.endpoints import my_entities

# Inside api/v1/api_router.py
v1_router.include_router(my_entities.router, prefix="/my-entities", tags=["My Entities"])
```

## Summary of Best Practices
1. **Never write DB queries in routers or services**: Always put them in `repositories/`.
2. **Never write business logic in routers**: Always call a `services/` method.
3. **Use Singletons**: Both repositories and services instantiate at the bottom of the file to be reused.
4. **Session Management**: Inject `AsyncSession` via `Depends(get_session)` in the endpoint, then pass it to the service (and repository) asynchronously.
5. **Exception Handling**: Use `fastapi.HTTPException` within services to return semantic HTTP errors (like 400 Bad Request or 401 Unauthorized) when business rules fail.
