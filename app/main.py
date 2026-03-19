from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse, HTMLResponse

from .dashboard import get_dashboard_html
from .docs_page import get_docs_html
from .metrics import instrumentator
from .routes import router

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
    docs_url=None,   # desabilitado — servimos nossa própria página
    redoc_url=None,
    openapi_tags=openapi_tags,
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
def health():
    return {"status": "healthy"}


instrumentator.instrument(app)
instrumentator.expose(app, include_in_schema=True)
