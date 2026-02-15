from app.domain.carts.models import MstCart
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.domain.carts.schemas import CartCreate, CartUpdate, CartDelete
from typing import Optional
from uuid import UUID

class CartRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_cart(self, cart_in: CartCreate) -> MstCart:
        new_cart = MstCart(
            id_user=cart_in.id_user,
            id_product=cart_in.id_product,
            quantity=cart_in.quantity,
            price_at_time=cart_in.price_at_time
        )
        self.db.add(new_cart)
        await self.db.commit()
        await self.db.refresh(new_cart)
        return new_cart

    async def update_cart(self, cart_id: UUID, cart_in: CartUpdate) -> Optional[MstCart]:
        result = await self.db.execute(select(MstCart).where(MstCart.id_cart == cart_id))
        cart = result.scalars().first()
        if not cart:
            return None
            
        update_data = cart_in.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(cart, key, value)

        self.db.add(cart)
        await self.db.commit()
        await self.db.refresh(cart)
        return cart
    
    async def get_carts_by_user_id(self, user_id: UUID, limit: int = 10, offset: int = 0) -> list[MstCart]:
        result = await self.db.execute(select(MstCart).where(MstCart.id_user == user_id).limit(limit).offset(offset))
        return result.scalars().all()
    
    async def delete_cart_each_item(self, cart_in: CartDelete) -> bool:
        result = await self.db.execute(select(MstCart).where(
            MstCart.id_product == cart_in.id_product,
            MstCart.id_user == cart_in.id_user
        ))
        cart = result.scalars().first()
        if not cart:
            return False
        self.db.delete(cart)
        await self.db.commit()
        return True
    
    async def empty_cart_by_user_id(self, user_id: UUID) -> bool:
        result = await self.db.execute(select(MstCart).where(MstCart.id_user == user_id))
        carts = result.scalars().all()
        if not carts:
            return False
        for cart in carts:
            self.db.delete(cart)
        await self.db.commit()
        return True