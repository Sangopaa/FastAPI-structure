from typing import TypeVar, Generic, Type, Any, Optional, List, Tuple
from sqlmodel import SQLModel, select, func
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

T = TypeVar("T", bound=SQLModel)


class BaseRepository(Generic[T]):
    def __init__(self, model: Type[T]):
        self.model = model

    async def get_all(
        self,
        session: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        sort_by: Optional[str] = None,
        sort_order: str = "asc",
        filter_by: Optional[str] = None,
        filter_value: Optional[Any] = None,
    ) -> Tuple[List[T], int]:
        query = select(self.model)

        if hasattr(self.model, "is_deleted"):
            query = query.where(self.model.is_deleted == False)

        if filter_by and hasattr(self.model, filter_by) and filter_value is not None:
            column = getattr(self.model, filter_by)
            query = query.where(column == filter_value)

        if sort_by and hasattr(self.model, sort_by):
            column = getattr(self.model, sort_by)
            if sort_order.lower() == "desc":
                query = query.order_by(column.desc())
            else:
                query = query.order_by(column.asc())

        count_query = select(func.count()).select_from(query.subquery())
        total_result = await session.execute(count_query)
        total = total_result.scalar() or 0

        data_result = await session.execute(query.offset(skip).limit(limit))
        data = data_result.scalars().all()

        return data, total

    async def get_by_id(self, session: AsyncSession, id: UUID) -> Optional[T]:
        query = select(self.model).where(
            self.model.id == id, self.model.is_deleted == False
        )
        result = await session.execute(query)
        return result.scalars().first()

    async def create(self, session: AsyncSession, obj_in: T) -> T:
        session.add(obj_in)
        await session.commit()
        await session.refresh(obj_in)
        return obj_in

    async def update(self, session: AsyncSession, db_obj: T, obj_in: Any) -> T:
        obj_data = (
            obj_in if isinstance(obj_in, dict) else obj_in.dict(exclude_unset=True)
        )
        for field, value in obj_data.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)

        session.add(db_obj)
        await session.commit()
        await session.refresh(db_obj)
        return db_obj

    async def delete(self, session: AsyncSession, db_obj: T) -> T:
        db_obj.is_deleted = True
        session.add(db_obj)
        await session.commit()
        await session.refresh(db_obj)
        return db_obj
