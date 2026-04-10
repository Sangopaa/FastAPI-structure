from core.generic_routes import GenericCRUDRouter
from models.accounts.user import User
from configurations.database import get_session


class UserRouter(GenericCRUDRouter[User]):
    def __init__(self):
        super().__init__(model=User, get_session=get_session)
        self.add_api_route("/me/profile", self.get_me, methods=["GET"])

    async def get_me(self):
        return {"user": "current_user_data"}


router = UserRouter()
