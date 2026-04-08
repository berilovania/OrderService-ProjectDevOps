from datetime import datetime, timezone
from enum import Enum
from uuid import uuid4

from pydantic import BaseModel, Field


class OrderStatus(str, Enum):
    created = "created"
    processing = "processing"
    completed = "completed"
    cancelled = "cancelled"


class OrderCreate(BaseModel):
    customer: str = Field(..., min_length=1, max_length=255)
    items: list[str] = Field(..., min_length=1, max_length=100)
    total: float = Field(..., gt=0, le=999_999.99)


class StatusUpdate(BaseModel):
    status: OrderStatus


class Order(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    customer: str
    items: list[str]
    total: float
    status: OrderStatus = OrderStatus.created
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
