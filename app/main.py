import asyncio
import os
from contextlib import asynccontextmanager
from datetime import datetime, timedelta, timezone
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse, HTMLResponse

from .dashboard import get_dashboard_html
from .database import engine, init_db, async_session
from .docs_page import get_docs_html
from .metrics import instrumentator
from .routes import router

DATA_RETENTION_HOURS = int(os.getenv("DATA_RETENTION_HOURS", "24"))


async def cleanup_old_orders():
    from sqlalchemy import delete
    from .db_models import OrderTable

    while True:
        await asyncio.sleep(3600)
        cutoff = datetime.now(timezone.utc) - timedelta(hours=DATA_RETENTION_HOURS)
        async with async_session() as session:
            await session.execute(
                delete(OrderTable).where(OrderTable.created_at < cutoff)
            )
            await session.commit()


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    cleanup_task = asyncio.create_task(cleanup_old_orders())
    yield
    cleanup_task.cancel()
    await engine.dispose()


openapi_tags = [
    {
        "name": "Orders",
        "description": "CRUD operations for order management",
    }
]

app = FastAPI(
    title="Order Service",
    description="REST API for order management | DevOps Project",
    version="1.0.0",
    docs_url=None,
    redoc_url=None,
    openapi_tags=openapi_tags,
    lifespan=lifespan,
)

app.include_router(router)


@app.get("/", response_class=HTMLResponse, include_in_schema=False)
def root():
    return get_dashboard_html()


@app.get("/docs", response_class=HTMLResponse, include_in_schema=False)
def docs():
    return get_docs_html()


@app.get("/favicon.ico", include_in_schema=False)
def favicon():
    path = Path(__file__).resolve().parent.parent / "favicon.ico"
    if path.exists():
        return FileResponse(path, media_type="image/x-icon")
    return HTMLResponse(status_code=204)


@app.get("/health")
async def health():
    from sqlalchemy import text

    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        return {"status": "healthy", "database": "connected"}
    except Exception:
        return {"status": "unhealthy", "database": "disconnected"}


instrumentator.instrument(app)
instrumentator.expose(app, include_in_schema=True)
