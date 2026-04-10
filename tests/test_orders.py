import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app


@pytest.mark.asyncio
async def test_health_check():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


@pytest.mark.asyncio
async def test_criar_pedido():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        payload = {"customer": "Alice", "items": ["notebook"], "total": 4500.00}
        response = await client.post("/orders", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["customer"] == "Alice"
    assert "id" in data


@pytest.mark.asyncio
async def test_listar_pedidos():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/orders")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_pedido_nao_encontrado():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/orders/00000000-0000-0000-0000-000000000000")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_pagina_inicial_tem_link_grafana():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "/grafana" in response.text


@pytest.mark.asyncio
async def test_pagina_inicial_tem_link_docs():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/")
    assert response.status_code == 200
    assert "/docs" in response.text


@pytest.mark.asyncio
async def test_security_headers_presentes():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/health")
    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert response.headers["X-Frame-Options"] == "DENY"
    assert "default-src" in response.headers["Content-Security-Policy"]
    assert response.headers["Referrer-Policy"] == "strict-origin-when-cross-origin"
    assert response.headers["Permissions-Policy"] == "camera=(), microphone=(), geolocation=()"


@pytest.mark.asyncio
async def test_rejeitar_customer_vazio():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        payload = {"customer": "", "items": ["notebook"], "total": 100.0}
        response = await client.post("/orders", json=payload)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_rejeitar_customer_muito_longo():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        payload = {"customer": "A" * 256, "items": ["notebook"], "total": 100.0}
        response = await client.post("/orders", json=payload)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_rejeitar_total_negativo():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        payload = {"customer": "Alice", "items": ["notebook"], "total": -10.0}
        response = await client.post("/orders", json=payload)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_rejeitar_total_zero():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        payload = {"customer": "Alice", "items": ["notebook"], "total": 0}
        response = await client.post("/orders", json=payload)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_rejeitar_items_vazio():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        payload = {"customer": "Alice", "items": [], "total": 100.0}
        response = await client.post("/orders", json=payload)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_rejeitar_items_demais():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        payload = {"customer": "Alice", "items": [f"item{i}" for i in range(101)], "total": 100.0}
        response = await client.post("/orders", json=payload)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_rejeitar_total_excessivo():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        payload = {"customer": "Alice", "items": ["notebook"], "total": 10_000_000.0}
        response = await client.post("/orders", json=payload)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_rejeitar_order_id_invalido():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/orders/not-a-uuid")
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_rejeitar_order_id_invalido_no_patch():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.patch("/orders/not-a-uuid/status", json={"status": "processing"})
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_rejeitar_order_id_invalido_no_delete():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.delete("/orders/not-a-uuid")
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_request_id_gerado_automaticamente():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/health")
    assert "X-Request-ID" in response.headers
    # Verify it's a valid UUID
    import uuid
    uuid.UUID(response.headers["X-Request-ID"])


@pytest.mark.asyncio
async def test_request_id_preservado_quando_enviado():
    custom_id = "test-request-123"
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/health", headers={"X-Request-ID": custom_id})
    assert response.headers["X-Request-ID"] == custom_id


@pytest.mark.asyncio
async def test_transicao_invalida_completed_para_processing():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Create order
        payload = {"customer": "Transition Test", "items": ["item"], "total": 100.0}
        create_resp = await client.post("/orders", json=payload)
        order_id = create_resp.json()["id"]
        # Move to processing
        await client.patch(f"/orders/{order_id}/status", json={"status": "processing"})
        # Move to completed
        await client.patch(f"/orders/{order_id}/status", json={"status": "completed"})
        # Try to go back to processing — should fail
        response = await client.patch(f"/orders/{order_id}/status", json={"status": "processing"})
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_transicao_invalida_completed_para_created():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        payload = {"customer": "Transition Test 2", "items": ["item"], "total": 50.0}
        create_resp = await client.post("/orders", json=payload)
        order_id = create_resp.json()["id"]
        await client.patch(f"/orders/{order_id}/status", json={"status": "processing"})
        await client.patch(f"/orders/{order_id}/status", json={"status": "completed"})
        response = await client.patch(f"/orders/{order_id}/status", json={"status": "created"})
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_transicao_valida_created_processing_completed():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        payload = {"customer": "Happy Path", "items": ["item"], "total": 200.0}
        create_resp = await client.post("/orders", json=payload)
        order_id = create_resp.json()["id"]
        r1 = await client.patch(f"/orders/{order_id}/status", json={"status": "processing"})
        r2 = await client.patch(f"/orders/{order_id}/status", json={"status": "completed"})
    assert r1.status_code == 200
    assert r2.status_code == 200


@pytest.mark.asyncio
async def test_health_nao_expoe_detalhes_do_banco():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/health")
    data = response.json()
    assert "database" not in data
    assert data["status"] == "healthy"


@pytest.mark.asyncio
async def test_cancelar_pedido_completed_rejeitado():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        payload = {"customer": "Cancel Test", "items": ["item"], "total": 100.0}
        create_resp = await client.post("/orders", json=payload)
        order_id = create_resp.json()["id"]
        await client.patch(f"/orders/{order_id}/status", json={"status": "processing"})
        await client.patch(f"/orders/{order_id}/status", json={"status": "completed"})
        response = await client.delete(f"/orders/{order_id}")
    assert response.status_code == 400
