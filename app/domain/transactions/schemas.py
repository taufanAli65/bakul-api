from enum import Enum
from pydantic import BaseModel
from typing import Optional
from uuid import UUID

class TransactionStatus(str, Enum):
    PAID = "paid"
    PENDING = "pending"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PACKING = "packing"
    COMPLETED = "completed"
    SHIPPED = "shipped"

class TransactionItem(BaseModel):
    id_product: UUID
    quantity: int
    price_at_time: Optional[int] = None


class TransactionCreate(BaseModel):
    id_user: UUID
    id_expedition_service: UUID
    items: Optional[list[TransactionItem]] = None


class TransactionCreateRequest(BaseModel):
    id_expedition_service: UUID
    items: Optional[list[TransactionItem]] = None


class TransactionStatusUpdate(BaseModel):
    status: TransactionStatus


class TransactionPaymentSimulation(BaseModel):
    transaction_id: UUID