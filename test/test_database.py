import pytest
from unittest.mock import AsyncMock, MagicMock, patch, create_autospec
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker
from typing import AsyncGenerator, AsyncIterator
from contextlib import asynccontextmanager
#from src.database import DatabaseSessionManager
from src.config import DatabaseConfig 


class MockAsyncSession:
    """
    Mock for AsyncSession
    """
    def __init__(self):
        self.mock_session = create_autospec(AsyncSession, instance=True)
        self.mock_session.execute = AsyncMock()
        self.mock_session.commit = AsyncMock()
        self.mock_session.rollback = AsyncMock()
        self.mock_session.close = AsyncMock()

    async def execute(self, *args, **kwargs):
        return await self.mock_session.execute(*args, **kwargs)
    
    async def commit(self, *args, **kwargs):
        return await self.mock_session.commit(*args, **kwargs)
    
    async def rollback(self, *args, **kwargs):
        return await self.mock_session.rollback(*args, **kwargs)
    
    async def close(self, *args, **kwargs):
        return await self.mock_session.close(*args, **kwargs)
    
    def __call__(self):
        return self.mock_session

@asynccontextmanager
async def async_context_manager_mock():
    yield

@pytest.fixture
def db_manager():
    mock_engine = patch('sqlalchemy.ext.asyncio.create_async_engine', return_value=AsyncMock(AsyncEngine)).start()
    mock_sessionmaker = patch('sqlalchemy.ext.asyncio.async_sessionmaker', return_value=MockAsyncSession()).start()
    from src.database import DatabaseSessionManager
    db_session_manager = DatabaseSessionManager()
    return db_session_manager, mock_engine, mock_sessionmaker

@pytest.mark.asyncio
async def test_init(db_manager):
        database_ses_men, mock_engine, mock_sessionmaker = db_manager
        #database_ses_men.init(DatabaseConfig.get_url())
        mock_engine.assert_called_once_with(DatabaseConfig.get_url())
        mock_sessionmaker.assert_called_once_with(autocommit=False, bind=mock_engine.return_value, class_=AsyncSession)
        mock_engine.reset_mock()
        mock_sessionmaker.reset_mock()

@pytest.mark.asyncio
async def test_close(db_manager):
    db_manager[0].init(DatabaseConfig.get_url())
    await db_manager[0].close()
    assert db_manager[0]._engine is None
    assert db_manager[0]._sessionmaker is None

@pytest.mark.asyncio
async def test_close_not_initialized(db_manager):
    with pytest.raises(Exception, match="DatabaseSessionManager is not initialized"):
        await db_manager[0].close()

@pytest.mark.asyncio
async def test_connect(db_manager):
    db_manager[0].init(DatabaseConfig.get_url())
    async with db_manager[0].connect() as connection:
        assert connection is not None

@pytest.mark.asyncio
async def test_connect_not_initialized(db_manager):
    with pytest.raises(Exception, match="DatabaseSessionManager is not initialized"):
        async with db_manager[0].connect() as connection:
            pass

@pytest.mark.asyncio
async def test_session(db_manager):
    db_manager[0].init(DatabaseConfig.get_url())
    async with db_manager[0].session() as session:
        assert session is not None
    db_manager[0]._sessionmaker.mock_session.commit.assert_awaited_once()
    db_manager[0]._sessionmaker.mock_session.close.assert_awaited_once()

@pytest.mark.asyncio
async def test_session_not_initialized(db_manager):
    with pytest.raises(Exception, match="DatabaseSessionManager is not initialized"):
        async with db_manager[0].session() as session:
            pass