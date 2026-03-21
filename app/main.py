import asyncio
import os
from contextlib import asynccontextmanager
from datetime import datetime, timedelta, timezone
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, HTMLResponse, PlainTextResponse

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


app = FastAPI(
    title="Order Service",
    description="REST API for order management | DevOps Project",
    version="2.0.0",
    docs_url=None,
    redoc_url=None,
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


@app.get("/health", include_in_schema=False)
async def health():
    from fastapi.responses import JSONResponse
    from sqlalchemy import text

    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        return {"status": "healthy", "database": "connected"}
    except Exception:
        return JSONResponse(
            status_code=503,
            content={"status": "unhealthy", "database": "disconnected"},
        )


instrumentator.instrument(app)

API_KEY = os.getenv("API_KEY", "")


@app.get("/metrics", include_in_schema=False)
async def metrics_endpoint(request: Request):
    client_ip = request.client.host if request.client else ""
    is_internal = client_ip in ("127.0.0.1", "::1") or client_ip.startswith(("10.", "172."))

    api_key = request.headers.get("X-API-Key", "")
    has_valid_key = bool(API_KEY) and api_key == API_KEY

    if not (is_internal or has_valid_key):
        raise HTTPException(status_code=403, detail="Forbidden")

    from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

    return PlainTextResponse(generate_latest(), media_type=CONTENT_TYPE_LATEST)
