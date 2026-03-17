from models.base_model import BaseModel


class User(BaseModel):
    email: str
    password: str
