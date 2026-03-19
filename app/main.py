from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from .dashboard import get_dashboard_html
from .metrics import instrumentator
from .routes import router

app = FastAPI(
    title="Order Service",
    description="API REST de gerenciamento de pedidos — Projeto DevOps",
    version="1.0.0",
    docs_url="/docs",
    redoc_url=None,
)

app.include_router(router)


@app.get("/", response_class=HTMLResponse)
def root():
    return get_dashboard_html()


@app.get("/health")
def health():
    return {"status": "healthy"}


instrumentator.instrument(app)
instrumentator.expose(app, include_in_schema=True)
