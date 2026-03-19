import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app


@pytest.mark.asyncio(loop_scope="session")
async def test_health_check():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


@pytest.mark.asyncio(loop_scope="session")
async def test_criar_pedido():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        payload = {"customer": "Alice", "items": ["notebook"], "total": 4500.00}
        response = await client.post("/orders", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["customer"] == "Alice"
    assert "id" in data


@pytest.mark.asyncio(loop_scope="session")
async def test_listar_pedidos():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/orders")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio(loop_scope="session")
async def test_pedido_nao_encontrado():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/orders/00000000-0000-0000-0000-000000000000")
    assert response.status_code == 404
