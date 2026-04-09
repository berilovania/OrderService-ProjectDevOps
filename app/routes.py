from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .database import get_db
from .db_models import OrderTable
from .models import Order, OrderCreate, OrderStatus, StatusUpdate
import logging

logger = logging.getLogger("order_service.routes")

router = APIRouter()

ALLOWED_TRANSITIONS: dict[str, set[str]] = {
    "created": {"processing", "cancelled"},
    "processing": {"completed", "cancelled"},
    "completed": set(),
    "cancelled": set(),
}


@router.post("/orders", response_model=Order, status_code=201,
             summary="Criar pedido (Create order)",
             description="Cria um novo pedido no sistema (Creates a new order)")
async def create_order(payload: OrderCreate, db: AsyncSession = Depends(get_db)):
    order = Order(**payload.model_dump())
    row = OrderTable(
        id=order.id,
        customer=order.customer,
        items=order.items,
        total=order.total,
        status=order.status.value,
        created_at=order.created_at,
    )
    db.add(row)
    await db.commit()
    logger.info(
        "Order created",
        extra={
            "action": "create_order",
            "order_id": str(order.id),
            "client_ip": "",
        },
    )
    return order


@router.get("/orders", response_model=list[Order],
            summary="Listar pedidos (List orders)",
            description="Retorna todos os pedidos com paginação (Returns all orders with pagination)")
async def list_orders(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(OrderTable).order_by(OrderTable.created_at.desc()).offset(skip).limit(limit)
    )
    rows = result.scalars().all()
    return [_row_to_order(r) for r in rows]


@router.get("/orders/{order_id}", response_model=Order,
            summary="Buscar pedido (Get order)",
            description="Busca um pedido pelo ID (Gets an order by ID)")
async def get_order(order_id: UUID, db: AsyncSession = Depends(get_db)):
    row = await db.get(OrderTable, str(order_id))
    if row is None:
        raise HTTPException(status_code=404, detail="Order not found")
    return _row_to_order(row)


@router.patch("/orders/{order_id}/status", response_model=Order,
              summary="Atualizar status (Update status)",
              description="Atualiza o status de um pedido (Updates an order status)")
async def update_order_status(
    order_id: UUID, payload: StatusUpdate, db: AsyncSession = Depends(get_db)
):
    row = await db.get(OrderTable, str(order_id))
    if row is None:
        raise HTTPException(status_code=404, detail="Order not found")
    allowed = ALLOWED_TRANSITIONS.get(row.status, set())
    if payload.status.value not in allowed:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot transition from '{row.status}' to '{payload.status.value}'",
        )
    row.status = payload.status.value
    await db.commit()
    logger.info(
        "Order status updated",
        extra={
            "action": "update_status",
            "order_id": str(order_id),
        },
    )
    await db.refresh(row)
    return _row_to_order(row)


@router.delete("/orders/{order_id}", response_model=Order,
               summary="Cancelar pedido (Cancel order)",
               description="Cancela um pedido existente (Cancels an existing order)")
async def cancel_order(order_id: UUID, db: AsyncSession = Depends(get_db)):
    row = await db.get(OrderTable, str(order_id))
    if row is None:
        raise HTTPException(status_code=404, detail="Order not found")
    row.status = OrderStatus.cancelled.value
    await db.commit()
    logger.info(
        "Order cancelled",
        extra={
            "action": "cancel_order",
            "order_id": str(order_id),
        },
    )
    await db.refresh(row)
    return _row_to_order(row)


def _row_to_order(row: OrderTable) -> Order:
    return Order(
        id=row.id,
        customer=row.customer,
        items=list(row.items),
        total=row.total,
        status=OrderStatus(row.status),
        created_at=row.created_at,
    )
