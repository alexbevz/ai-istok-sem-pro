import contextlib
from typing import AsyncIterator

from src.config import DatabaseConfig

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker, AsyncConnection, AsyncEngine

db_config = DatabaseConfig()

# db_engine = create_async_engine(url=db_config.get_url(), echo=False, future=True)
#
# async_session = async_sessionmaker(
#     bind=db_engine,  expire_on_commit=False, class_=AsyncSession
#)


class DatabaseSessionManager:
    def __init__(self):
        self._engine: AsyncEngine | None = None
        self._sessionmaker: async_sessionmaker | None = None

    def init(self, host: str):
        self._engine = create_async_engine(host)
        self._sessionmaker = async_sessionmaker(autocommit=False, bind=self._engine, class_=AsyncSession)

    async def close(self):
        if self._engine is None:
            raise Exception("DatabaseSessionManager is not initialized")
        await self._engine.dispose()
        self._engine = None
        self._sessionmaker = None

    @contextlib.asynccontextmanager
    async def connect(self) -> AsyncIterator[AsyncConnection]:
        if self._engine is None:
            raise Exception("DatabaseSessionManager is not initialized")

        async with self._engine.begin() as connection:
            try:
                yield connection
            except Exception:
                await connection.rollback()
                raise

    @contextlib.asynccontextmanager
    async def session(self) -> AsyncIterator[AsyncSession]:
        if self._sessionmaker is None:
            raise Exception("DatabaseSessionManager is not initialized")

        session = self._sessionmaker()
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


db_session_manager = DatabaseSessionManager()
db_session_manager.init(db_config.get_url())


async def get_session_db() -> AsyncIterator[AsyncSession]:
    async with db_session_manager.session() as session:
        yield session



# def get_sync_session_db() -> AsyncSession:
#     return async_session()
