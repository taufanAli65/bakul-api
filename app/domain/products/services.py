from typing import Optional
from app.domain.products.repositories import ProductRepository
from app.domain.products.schemas import ProductCreate, ProductUpdate
from app.domain.products.models import MstProduct, TrnProductStock
from uuid import UUID

class ProductService:
    def __init__(self, product_repo: ProductRepository):
        self.product_repo = product_repo

    async def create_product(self, product_in: ProductCreate) -> MstProduct:
        return await self.product_repo.create_product(
            name=product_in.name,
            description=product_in.description,
            price=product_in.price,
            stock=product_in.stock,
            product_image_url=product_in.product_image_url,
        )

    async def update_product(self, product_id: UUID, product_in: ProductUpdate) -> Optional[MstProduct]:
        return await self.product_repo.update_product(
            product_id,
            name=product_in.name,
            description=product_in.description,
            price=product_in.price,
            product_image_url=product_in.product_image_url,
        )

    async def update_product_stock(self, product_id: UUID, stock: int) -> Optional[TrnProductStock]:
        return await self.product_repo.update_product_stock(product_id, stock)

    async def get_product_by_id(self, product_id: UUID) -> Optional[MstProduct]:
        return await self.product_repo.get_product_by_id(product_id)
    
    async def get_all_products(self, limit: int = 10, offset: int = 0) -> list[MstProduct]:
        return await self.product_repo.get_all_products(limit, offset)
    
    async def delete_product(self, product_id: UUID) -> bool:
        return await self.product_repo.delete_product(product_id)