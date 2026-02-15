from app.domain.carts.models import MstCart
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import Optional
from uuid import UUID

class CartRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_cart(self, id_user: UUID, id_product: UUID, quantity: int, price_at_time: int) -> MstCart:
        new_cart = MstCart(
            id_user=id_user,
            id_product=id_product,
            quantity=quantity,
            price_at_time=price_at_time,
        )
        self.db.add(new_cart)
        await self.db.commit()
        await self.db.refresh(new_cart)
        return new_cart

    async def update_cart(
        self,
        cart_id: UUID,
        quantity: Optional[int] = None,
        price_at_time: Optional[int] = None,
    ) -> Optional[MstCart]:
        result = await self.db.execute(select(MstCart).where(MstCart.id_cart == cart_id))
        cart = result.scalars().first()
        if not cart:
            return None

        if quantity is not None:
            cart.quantity = quantity
        if price_at_time is not None:
            cart.price_at_time = price_at_time

        self.db.add(cart)
        await self.db.commit()
        await self.db.refresh(cart)
        return cart
    
    async def get_carts_by_user_id(self, user_id: UUID, limit: int = 10, offset: int = 0) -> list[MstCart]:
        result = await self.db.execute(select(MstCart).where(MstCart.id_user == user_id).limit(limit).offset(offset))
        return result.scalars().all()
    
    async def delete_cart_each_item(self, id_user: UUID, id_product: UUID) -> bool:
        result = await self.db.execute(select(MstCart).where(
            MstCart.id_product == id_product,
            MstCart.id_user == id_user,
        ))
        cart = result.scalars().first()
        if not cart:
            return False
        self.db.delete(cart)
        await self.db.commit()
        return True

    async def get_cart_by_id(self, cart_id: UUID) -> Optional[MstCart]:
        result = await self.db.execute(select(MstCart).where(MstCart.id_cart == cart_id))
        return result.scalars().first()
    
    async def empty_cart_by_user_id(self, user_id: UUID) -> bool:
        result = await self.db.execute(select(MstCart).where(MstCart.id_user == user_id))
        carts = result.scalars().all()
        if not carts:
            return False
        for cart in carts:
            self.db.delete(cart)
        await self.db.commit()
        return True