import pytest_asyncio
from app.database import init_db


@pytest_asyncio.fixture(scope="session", loop_scope="session", autouse=True)
async def setup_db():
    await init_db()
