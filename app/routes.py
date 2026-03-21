from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from .auth import require_api_key
from .database import get_db
from .db_models import OrderTable
from .models import Order, OrderCreate, OrderStatus, StatusUpdate

router = APIRouter()


@router.post("/orders", response_model=Order, status_code=201, dependencies=[Depends(require_api_key)],
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
    return order


@router.get("/orders", response_model=list[Order],
            summary="Listar pedidos (List orders)",
            description="Retorna todos os pedidos com paginação (Returns all orders with pagination)")
async def list_orders(
    skip: int = Query(0, ge=0),
    limit: int = Query(200, ge=1, le=1000),
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
async def get_order(order_id: str, db: AsyncSession = Depends(get_db)):
    row = await db.get(OrderTable, order_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Order not found")
    return _row_to_order(row)


@router.patch("/orders/{order_id}/status", response_model=Order, dependencies=[Depends(require_api_key)],
              summary="Atualizar status (Update status)",
              description="Atualiza o status de um pedido (Updates an order status)")
async def update_order_status(
    order_id: str, payload: StatusUpdate, db: AsyncSession = Depends(get_db)
):
    row = await db.get(OrderTable, order_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Order not found")
    if row.status == OrderStatus.cancelled.value:
        raise HTTPException(status_code=400, detail="Cannot update a cancelled order")
    row.status = payload.status.value
    await db.commit()
    await db.refresh(row)
    return _row_to_order(row)


@router.delete("/orders/{order_id}", response_model=Order, dependencies=[Depends(require_api_key)],
               summary="Cancelar pedido (Cancel order)",
               description="Cancela um pedido existente (Cancels an existing order)")
async def cancel_order(order_id: str, db: AsyncSession = Depends(get_db)):
    row = await db.get(OrderTable, order_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Order not found")
    row.status = OrderStatus.cancelled.value
    await db.commit()
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
