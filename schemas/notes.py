from pydantic import BaseModel
from uuid import UUID


class NoteBase(BaseModel):
    title: str
    content: str
    user_id: UUID


class NoteCreate(NoteBase):
    pass


class NoteRead(NoteBase):
    id: UUID
    is_deleted: bool

    class Config:
        from_attributes = True
