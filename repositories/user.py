from fastapi import Depends
from sqlmodel import Session

from configurations.database import get_session
from repositories.base_repository import BaseRepository
from models.auth.user import User


class UserRepository(BaseRepository[User]):
    def __init__(self, session: Session = Depends(get_session)):
        super().__init__(User, session)
