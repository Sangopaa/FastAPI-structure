from uuid import UUID
from models.base_model import BaseModel
from sqlmodel import Field


class Inversion(BaseModel):
    amount: int
    user_id: UUID | None = Field(default=None, foreign_key="auth.user.id")
