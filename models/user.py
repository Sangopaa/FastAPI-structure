from typing import Optional
from sqlmodel import Field
from models.base_model import BaseModel


class User(BaseModel):
    username: Optional[str] = Field(index=True, unique=True, nullable=True)
    email: str = Field(unique=True, index=True, nullable=False)
    full_name: Optional[str] = None
    hashed_password: Optional[str] = Field(default=None, nullable=True)
    google_id: Optional[str] = Field(default=None, index=True, nullable=True)
    avatar_url: Optional[str] = None
    is_active: bool = Field(default=True)
