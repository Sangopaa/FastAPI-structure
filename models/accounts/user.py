from typing import Optional
from sqlmodel import Field
from models.base_model import BaseModel
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class User(BaseModel):
    username: Optional[str] = Field(index=True, unique=True, nullable=True)
    email: str = Field(unique=True, index=True, nullable=False)
    full_name: Optional[str] = None
    hashed_password: Optional[str] = Field(default=None, nullable=True)
    google_id: Optional[str] = Field(default=None, index=True, nullable=True)
    avatar_url: Optional[str] = None
    is_active: bool = Field(default=True)

    def set_password(self, password: str):
        """Hash password"""
        self.hashed_password = pwd_context.hash(password)

    def verify_password(self, password: str) -> bool:
        """Compare text plain password with saved hash"""
        if not self.hashed_password:
            return False
        return pwd_context.verify(password, self.hashed_password)
