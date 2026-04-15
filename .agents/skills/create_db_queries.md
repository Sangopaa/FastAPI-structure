# Skill: Creating New Database Queries

This guide explains the standard procedure for creating new database queries within the repositories layer in our async FastAPI + SQLModel project.

## 1. Location of Queries
All database queries must be written in the `repositories/` directory. **Do not** write queries in services or routers.
- Each major context or model should have its own repository file (e.g., `repositories/users.py`, `repositories/products.py`).
- The repository must inherit from `repositories.base.BaseRepository`.

## 2. Using SQLModel and AsyncSession
We use `sqlmodel` for query building and `sqlalchemy.ext.asyncio.AsyncSession` for asynchronous execution.
Always remember to:
- Pass `session: AsyncSession` as an argument to every repository method.
- Use `await` for executing queries.
- Build the `select(...)` statements using `sqlmodel.select`.

## 3. Query Types
### Fetching Multiple Instances (`get_all`, `filter`)
When fetching multiple items, you'll need `.scalars().all()`.

```python
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

async def get_active_users(self, session: AsyncSession) -> List[User]:
    statement = select(self.model).where(self.model.is_active == True)
    result = await session.execute(statement)
    return result.scalars().all()
```

### Fetching a Single Instance (`get_by_id`, `get_by_email`)
When fetching a single item, use `.scalars().first()` or `.scalar_one_or_none()`.

```python
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

async def get_by_email(self, session: AsyncSession, email: str) -> Optional[User]:
    statement = select(self.model).where(self.model.email == email)
    result = await session.execute(statement)
    # .first() returns the first element or None
    return result.scalars().first()
```

### Executing Complex Queries (Joins, Aggregations)
For queries involving joins or grouped data, `session.execute` can be parsed.
If selecting specific columns, use `.all()` directly or parse the tuples.

```python
from sqlmodel import select, func
from sqlalchemy.ext.asyncio import AsyncSession

async def get_user_counts_by_status(self, session: AsyncSession):
    statement = select(
        self.model.status, func.count(self.model.id)
    ).group_by(self.model.status)

    result = await session.execute(statement)
    return result.all() # Returns a list of tuples like [('active', 10), ('inactive', 5)]
```

### Inserting and Updating Data
For single items, you can use the base methods inherited from `BaseRepository`, which typically do:

```python
async def update_status(self, session: AsyncSession, user_id: UUID, new_status: str):
    user = await self.get_by_id(session, user_id)
    if user:
        user.status = new_status
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user
    return None
```

## Summary
- Ensure all methods are `async def`.
- Accept `session: AsyncSession` as a parameter.
- Use `await session.execute(...)`.
- Call `.scalars().all()` for lists and `.scalars().first()` for a single item.
