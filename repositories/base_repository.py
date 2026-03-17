from typing import Generic, List, Optional, Type, TypeVar
from sqlmodel import SQLModel, Session, select

T = TypeVar("T", bound=SQLModel)


class BaseRepository(Generic[T]):
    def __init__(self, model: Type[T], session: Session):
        self.model = model
        self.session = session

    def get_by_id(self, item_id: int) -> Optional[T]:
        return self.session.get(self.model, item_id)

    def get_all(self, skip: int = 0, limit: int = 10) -> List[T]:
        statement = select(self.model).offset(skip).limit(limit)
        return self.session.exec(statement).all()
