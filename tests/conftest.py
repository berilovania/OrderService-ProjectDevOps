import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool

import app.database as db_module
import app.main as main_module
from app.db_models import Base
from app.database import DATABASE_URL


@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_db():
    # NullPool: connections are never cached between calls.
    # This eliminates "Future attached to a different loop" errors caused by
    # pytest-asyncio creating a separate event loop per test function.
    test_engine = create_async_engine(DATABASE_URL, poolclass=NullPool)
    test_session_maker = async_sessionmaker(test_engine, expire_on_commit=False)

    # Patch every module-level reference to the engine so the app uses NullPool.
    db_module.engine = test_engine
    db_module.async_session = test_session_maker
    main_module.engine = test_engine

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield

    await test_engine.dispose()
