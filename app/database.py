import os

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

DATABASE_HOST = os.getenv("DATABASE_HOST", "localhost")
DATABASE_PORT = os.getenv("DATABASE_PORT", "5432")
DATABASE_USER = os.getenv("DATABASE_USER", "orders")
DATABASE_PASSWORD = os.getenv("DATABASE_PASSWORD", "orders")
DATABASE_NAME = os.getenv("DATABASE_NAME", "orders")

DATABASE_URL = (
    f"postgresql+asyncpg://{DATABASE_USER}:{DATABASE_PASSWORD}"
    f"@{DATABASE_HOST}:{DATABASE_PORT}/{DATABASE_NAME}"
)

engine = create_async_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    connect_args={"timeout": 10},
)
async_session = async_sessionmaker(engine, expire_on_commit=False)


async def init_db():
    import asyncio
    from .db_models import Base

    for attempt in range(30):
        try:
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            return
        except Exception as exc:
            if attempt < 29:
                print(f"DB connection attempt {attempt + 1} failed: {exc} — retrying in 5s...")
                await asyncio.sleep(5)
            else:
                raise


async def get_db():
    async with async_session() as session:
        yield session
