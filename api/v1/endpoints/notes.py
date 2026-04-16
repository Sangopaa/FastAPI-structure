from core.generic_routes import GenericCRUDRouter
from models.notes.note import Note
from schemas.notes import NoteCreate, NoteRead
from configurations.database import get_session


class NoteRouter(GenericCRUDRouter[Note]):
    def __init__(self):
        super().__init__(
            model=Note,
            get_session=get_session,
            schema_create=NoteCreate,
            schema_read=NoteRead,
        )


router = NoteRouter()
