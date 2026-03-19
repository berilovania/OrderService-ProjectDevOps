from fastapi import APIRouter, HTTPException

from .models import Order, OrderCreate, OrderStatus, StatusUpdate

router = APIRouter(tags=["Orders"])

# In-memory storage
orders: dict[str, Order] = {}


@router.post("/orders", response_model=Order, status_code=201)
def create_order(payload: OrderCreate):
    order = Order(**payload.model_dump())
    orders[order.id] = order
    return order


@router.get("/orders", response_model=list[Order])
def list_orders():
    return list(orders.values())


@router.get("/orders/{order_id}", response_model=Order)
def get_order(order_id: str):
    if order_id not in orders:
        raise HTTPException(status_code=404, detail="Order not found")
    return orders[order_id]


@router.patch("/orders/{order_id}/status", response_model=Order)
def update_order_status(order_id: str, payload: StatusUpdate):
    if order_id not in orders:
        raise HTTPException(status_code=404, detail="Order not found")
    order = orders[order_id]
    if order.status == OrderStatus.cancelled:
        raise HTTPException(status_code=400, detail="Cannot update a cancelled order")
    order.status = payload.status
    return order


@router.delete("/orders/{order_id}", response_model=Order)
def cancel_order(order_id: str):
    if order_id not in orders:
        raise HTTPException(status_code=404, detail="Order not found")
    order = orders[order_id]
    order.status = OrderStatus.cancelled
    return order
