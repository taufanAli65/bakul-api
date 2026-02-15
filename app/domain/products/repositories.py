import uuid
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.domain.products.models import MstProduct, TrnProductStock
from app.domain.products.schemas import ProductBase, ProductCreate, ProductUpdate
from typing import Optional

class ProductRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    def create_product(self, product_in: ProductCreate) -> ProductBase:
        new_product = MstProduct(
            name=product_in.name,
            description=product_in.description,
            price=product_in.price,
            product_image_url=product_in.product_image_url
        )
        self.db.add(new_product)
        add_product_stock = TrnProductStock(
            id_product=new_product.id_product,
            stock=product_in.stock
        )
        self.db.add(add_product_stock)
        self.db.commit()
        self.db.refresh(new_product, add_product_stock)
        product_data = ProductBase(
            name=new_product.name,
            description=new_product.description,
            price=new_product.price,
            product_image_url=new_product.product_image_url,
            stock=add_product_stock.stock
        )
        return product_data

    def update_product(self, product_id: uuid.UUID, product_in: ProductUpdate) -> Optional[ProductBase]:
        result = self.db.execute(select(MstProduct).where(MstProduct.id_product == product_id))
        product = result.scalars().first()
        if not product:
            return None
        
        update_data = product_in.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(product, key, value)

        self.db.add(product)
        self.db.commit()
        self.db.refresh(product)
        return product
    
    def update_product_stock(self, product_id: uuid.UUID, stock: int) -> Optional[TrnProductStock]:
        result = self.db.execute(select(TrnProductStock).where(TrnProductStock.id_product == product_id))
        product_stock = result.scalars().first()
        if not product_stock:
            return None
        
        product_stock.stock = stock
        self.db.add(product_stock)
        self.db.commit()
        self.db.refresh(product_stock)
        return product_stock
    
    def get_product_by_id(self, product_id: uuid.UUID) -> Optional[ProductBase]:
        result = self.db.execute(select(MstProduct).where(MstProduct.id_product == product_id).join(TrnProductStock, MstProduct.id_product == TrnProductStock.id_product))
        product = result.scalars().first()
        if not product:
            return None
        return product
    
    def get_all_products(self, limit: int = 10, offset: int = 0) -> list[ProductBase]:
        result = self.db.execute(select(MstProduct).limit(limit).offset(offset).join(TrnProductStock, MstProduct.id_product == TrnProductStock.id_product))
        products = result.scalars().all()
        return products
    
    def delete_product(self, product_id: uuid.UUID) -> bool:
        result = self.db.execute(select(MstProduct).where(MstProduct.id_product == product_id))
        product = result.scalars().first()
        if not product:
            return False
        
        self.db.delete(product)
        self.db.commit()
        return True