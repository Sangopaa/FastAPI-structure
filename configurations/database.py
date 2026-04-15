import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()


class Database:
    def __init__(self):
        self._connection_string = os.getenv("CONNECTION_STRING")
        if not self._connection_string:
            raise ValueError("CONNECTION_STRING environment variable is not set")

        self.engine = create_async_engine(
            self._connection_string,
            pool_size=10,
            max_overflow=20,
            pool_pre_ping=True,
            echo=False,
        )

        self.async_session_maker = sessionmaker(
            self.engine, class_=AsyncSession, expire_on_commit=False
        )


db = Database()


async def get_session() -> AsyncSession:
    async with db.async_session_maker() as session:
        yield session
