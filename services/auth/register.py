from repositories.user import UserRepository
from base_service import BaseService


class RegisterService(BaseService):

    def __init__(self):
        self.repository = UserRepository()

    def execute(self):
        pass
