import asyncio
import ipaddress
from contextlib import asynccontextmanager
from datetime import datetime, timedelta, timezone
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse, PlainTextResponse

from .dashboard import get_dashboard_html
from .database import engine, init_db, async_session
from .docs_page import get_docs_html
from .metrics import instrumentator
from .routes import router

import os

DATA_RETENTION_HOURS = int(os.getenv("DATA_RETENTION_HOURS", "24"))
METRICS_TOKEN = os.getenv("METRICS_TOKEN", "")


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
    try:
        await cleanup_task
    except asyncio.CancelledError:
        pass
    await engine.dispose()


app = FastAPI(
    title="Order Service",
    description="API REST para gerenciamento de pedidos (Order management REST API) | Projeto DevOps",
    version="2.0.0",
    docs_url=None,
    redoc_url=None,
    lifespan=lifespan,
)

app.include_router(router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ALLOWED_ORIGINS", "").split(",") if os.getenv("CORS_ALLOWED_ORIGINS") else [],
    allow_methods=["GET", "POST", "PATCH", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)


@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
        "style-src 'self' 'unsafe-inline'; "
        "img-src 'self' data:; "
        "font-src 'self' data:"
    )
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
    return response


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


@app.get("/metrics", include_in_schema=False)
async def metrics_endpoint(request: Request):
    # Layer 1: Token-based authentication (if METRICS_TOKEN is configured)
    if METRICS_TOKEN:
        import hmac
        auth_header = request.headers.get("Authorization", "")
        token = auth_header.removeprefix("Bearer ").strip() if auth_header.startswith("Bearer ") else ""
        if not token or not hmac.compare_digest(token, METRICS_TOKEN):
            raise HTTPException(status_code=403, detail="Forbidden")
    else:
        # Layer 2 (fallback): IP-based restriction when no token is configured
        client_ip = request.client.host if request.client else ""
        try:
            _ip = ipaddress.ip_address(client_ip)
            is_internal = _ip.is_loopback or _ip.is_private
        except ValueError:
            is_internal = False

        if not is_internal:
            raise HTTPException(status_code=403, detail="Forbidden")

    from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

    return PlainTextResponse(generate_latest(), media_type=CONTENT_TYPE_LATEST)
