import uuid
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.domain.products.models import MstProduct, TrnProductStock
from app.domain.products.schemas import ProductCreate, ProductUpdate

class ProductRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_product(self, product_in: ProductCreate) -> MstProduct:
        new_product = MstProduct(
            name=product_in.name,
            description=product_in.description,
            price=product_in.price,
            product_image_url=product_in.product_image_url,
        )
        add_product_stock = TrnProductStock(
            id_product=new_product.id_product,
            stock=product_in.stock,
        )
        self.db.add_all([new_product, add_product_stock])
        await self.db.commit()
        await self.db.refresh(new_product)
        await self.db.refresh(add_product_stock)
        new_product.stock = add_product_stock.stock  # expose stock for response
        return new_product

    async def update_product(self, product_id: uuid.UUID, product_in: ProductUpdate) -> Optional[MstProduct]:
        result = await self.db.execute(select(MstProduct).where(MstProduct.id_product == product_id))
        product = result.scalars().first()
        if not product:
            return None

        update_data = product_in.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(product, key, value)

        self.db.add(product)
        await self.db.commit()
        await self.db.refresh(product)
        return product

    async def update_product_stock(self, product_id: uuid.UUID, stock: int) -> Optional[TrnProductStock]:
        result = await self.db.execute(select(TrnProductStock).where(TrnProductStock.id_product == product_id))
        product_stock = result.scalars().first()
        if not product_stock:
            return None

        product_stock.stock = stock
        self.db.add(product_stock)
        await self.db.commit()
        await self.db.refresh(product_stock)
        return product_stock

    async def get_product_by_id(self, product_id: uuid.UUID) -> Optional[MstProduct]:
        result = await self.db.execute(
            select(MstProduct, TrnProductStock.stock)
            .join(TrnProductStock, MstProduct.id_product == TrnProductStock.id_product)
            .where(MstProduct.id_product == product_id)
        )
        row = result.first()
        if not row:
            return None
        product, stock = row
        product.stock = stock
        return product

    async def get_all_products(self, limit: int = 10, offset: int = 0) -> list[MstProduct]:
        result = await self.db.execute(
            select(MstProduct, TrnProductStock.stock)
            .join(TrnProductStock, MstProduct.id_product == TrnProductStock.id_product)
            .limit(limit)
            .offset(offset)
        )
        products: list[MstProduct] = []
        for product, stock in result.all():
            product.stock = stock
            products.append(product)
        return products

    async def delete_product(self, product_id: uuid.UUID) -> bool:
        result = await self.db.execute(select(MstProduct).where(MstProduct.id_product == product_id))
        product = result.scalars().first()
        if not product:
            return False

        await self.db.delete(product)
        await self.db.commit()
        return True