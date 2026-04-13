from typing import TypeVar, Generic, Type, Any, Optional, List, Tuple
from sqlmodel import SQLModel, Session, select, func
from uuid import UUID

T = TypeVar("T", bound=SQLModel)


class BaseRepository(Generic[T]):
    def __init__(self, model: Type[T]):
        self.model = model

    def get_all(self, session: Session, skip: int = 0, limit: int = 100) -> Tuple[List[T], int]:
        total = session.scalar(select(func.count()).select_from(self.model))
        data = session.exec(select(self.model).offset(skip).limit(limit)).all()
        return data, total

    def get_by_id(self, session: Session, id: UUID) -> Optional[T]:
        return session.get(self.model, id)

    def create(self, session: Session, obj_in: Any) -> T:
        session.add(obj_in)
        session.commit()
        session.refresh(obj_in)
        return obj_in

    def update(self, session: Session, db_obj: T, obj_in: Any) -> T:
        obj_data = (
            obj_in if isinstance(obj_in, dict) else obj_in.dict(exclude_unset=True)
        )
        for field in obj_data:
            if hasattr(db_obj, field):
                setattr(db_obj, field, obj_data[field])
        session.add(db_obj)
        session.commit()
        session.refresh(db_obj)
        return db_obj

    def delete(self, session: Session, db_obj: T) -> T:
        db_obj.is_deleted = True
        session.add(db_obj)
        session.commit()
        session.refresh(db_obj)
        return db_obj
