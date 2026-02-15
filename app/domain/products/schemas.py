from pydantic import BaseModel
from typing import Optional

class ProductBase(BaseModel):
    name: str
    description: Optional[str]
    price: int
    product_image_url: Optional[str]
    stock: int

class ProductCreate(ProductBase):
    pass

class ProductUpdate(BaseModel):
    name: Optional[str]
    description: Optional[str]
    price: Optional[int]
    product_image_url: Optional[str]

class ProductUpdateStock(BaseModel):
    stock: int