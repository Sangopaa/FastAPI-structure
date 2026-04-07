from core.generic_routes import GenericCRUDRouter
from models.user import User
from configurations.database import get_session
from sqlmodel import Session


class UserRouter(GenericCRUDRouter[User]):
    def __init__(self):
        super().__init__(model=User, get_session=get_session)
        self.add_api_route("/me/profile", self.get_me, methods=["GET"])

    async def get_me(self):
        return {"user": "current_user_data"}

    async def create(self, session: Session, obj: User):
        obj.hashed_password = f"secret_{obj.hashed_password}"
        return await super().create(session, obj)


router = UserRouter()
