import contextlib
from typing import AsyncIterator
from sqlalchemy import MetaData
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
    AsyncConnection,
)
from sqlalchemy.orm import DeclarativeBase
from ..config import settings

CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


class Base(DeclarativeBase):
    metadata = MetaData(naming_convention=CONVENTION)


class DatabaseSessionManager:
    """Database session manager for handling database connections and sessions.

    This class provides methods to create and manage database sessions, as well as to create and drop database tables.
    This is a powerful tool for managing database connections in an asynchronous environment and encapsulates the logic for handling database sessions and connections.
    """

    def __init__(self, url: str):
        self._engine: AsyncEngine = create_async_engine(url)
        self._sessionmaker: AsyncSession = async_sessionmaker(
            autocommit=False,
            bind=self._engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )

    async def close(self):
        if self._engine is None:
            raise Exception("Engine is not initialized.")
        await self._engine.dispose()
        self._engine = None
        self._sessionmaker = None

    @contextlib.asynccontextmanager
    async def connect(self) -> AsyncIterator[AsyncConnection]:
        if self._engine is None:
            raise Exception("Engine is not initialized.")

        async with self._engine.connect() as connection:
            try:
                yield connection
            except Exception as e:
                await connection.rollback()
                raise e
            finally:
                await connection.close()

    @contextlib.asynccontextmanager
    async def session(self) -> AsyncIterator[AsyncSession]:
        if self._sessionmaker is None:
            raise Exception("Sessionmaker is not initialized.")

        session = self._sessionmaker()
        try:
            yield session
        except Exception as e:
            await session.rollback()
            raise e
        finally:
            await session.close()

    async def create_all(self, connection: AsyncConnection):
        await connection.run_sync(Base.metadata.create_all)

    async def drop_all(self, connection: AsyncConnection):
        await connection.run_sync(Base.metadata.drop_all)


sessionmanager = DatabaseSessionManager(settings.DB_URL.unicode_string())
