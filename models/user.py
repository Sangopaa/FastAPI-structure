from typing import Optional
from sqlmodel import Field
from models.base_model import BaseModel


class User(BaseModel):
    username: str = Field(index=True, unique=True, nullable=False)
    email: str = Field(unique=True, index=True, nullable=False)
    full_name: Optional[str] = None
    hashed_password: str = Field(nullable=False)
    is_active: bool = Field(default=True)
