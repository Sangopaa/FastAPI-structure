from typing import Optional
from sqlmodel import Session, select
from models.accounts.user import User
from repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    def __init__(self):
        super().__init__(User)

    async def get_by_email(self, session: Session, email: str) -> Optional[User]:
        statement = select(self.model).where(self.model.email == email)
        result = await session.execute(statement)
        return result.scalars().first()


user_repository = UserRepository()
