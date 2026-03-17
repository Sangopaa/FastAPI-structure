import os

from sqlmodel import create_engine, Session
from dotenv import load_dotenv

load_dotenv()


class Database:
    def __init__(self):
        self._connection_string = os.getenv("CONNECTION_STRING")
        if not self._connection_string:
            raise ValueError("CONNECTION_STRING environment variable is not set")

        self.engine = create_engine(
            self._connection_string, pool_size=10, max_overflow=20, pool_pre_ping=True
        )


db = Database()


def get_session():
    with Session(db.engine) as session:
        yield session
