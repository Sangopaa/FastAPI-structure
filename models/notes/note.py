from sqlmodel import Field, Relationship
from models.base_model import BaseModel
from uuid import UUID


class Note(BaseModel):
    title: str = Field(index=True)
    content: str

    user_id: UUID = Field(foreign_key="accounts.user.id")
    author: "User" = Relationship(back_populates="notes")
