from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from .dashboard import get_dashboard_html
from .docs_page import get_docs_html
from .metrics import instrumentator
from .routes import router

app = FastAPI(
    title="Order Service",
    description="REST API for order management | DevOps Project",
    version="1.0.0",
    docs_url=None,   # desabilitado — servimos nossa própria página
    redoc_url=None,
)

app.include_router(router)


@app.get("/", response_class=HTMLResponse, include_in_schema=False)
def root():
    return get_dashboard_html()


@app.get("/docs", response_class=HTMLResponse, include_in_schema=False)
def docs():
    return get_docs_html()


@app.get("/health")
def health():
    return {"status": "healthy"}


instrumentator.instrument(app)
instrumentator.expose(app, include_in_schema=True)
