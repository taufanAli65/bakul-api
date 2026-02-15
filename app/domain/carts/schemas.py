from pydantic import BaseModel
from typing import Optional
from uuid import UUID

class CartBase(BaseModel):
    id_product: UUID
    id_user: UUID
    quantity: int
    price_at_time: int

class CartCreate(CartBase):
    pass

class CartUpdate(BaseModel):
    id_product: Optional[UUID]
    quantity: Optional[int]
    price_at_time: Optional[int]

class CartDelete(BaseModel):
    id_product: UUID
    id_user: UUID