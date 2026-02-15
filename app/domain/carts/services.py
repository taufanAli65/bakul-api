from app.domain.carts.models import MstCart
from app.domain.carts.repositories import CartRepository
from app.domain.carts.schemas import CartCreate, CartUpdate, CartDelete
from typing import Optional, List
from uuid import UUID

class CartService:
    def __init__(self, cart_repo: CartRepository):
        self.cart_repo = cart_repo

    async def create_cart(self, cart_in: CartCreate) -> MstCart:
        return await self.cart_repo.create_cart(
            id_user=cart_in.id_user,
            id_product=cart_in.id_product,
            quantity=cart_in.quantity,
            price_at_time=cart_in.price_at_time,
        )

    async def update_cart(self, cart_id: UUID, cart_in: CartUpdate) -> Optional[MstCart]:
        return await self.cart_repo.update_cart(
            cart_id,
            quantity=cart_in.quantity,
            price_at_time=cart_in.price_at_time,
        )
    
    async def get_carts_by_user_id(self, user_id: UUID, limit: int = 10, offset: int = 0) -> List[MstCart]:
        return await self.cart_repo.get_carts_by_user_id(user_id, limit=limit, offset=offset)
    
    async def delete_cart_each_item(self, cart_in: CartDelete) -> bool:
        return await self.cart_repo.delete_cart_each_item(
            id_user=cart_in.id_user,
            id_product=cart_in.id_product,
        )
    
    async def empty_cart_by_user_id(self, user_id: UUID) -> bool:
        return await self.cart_repo.empty_cart_by_user_id(user_id)

    async def get_cart_by_id(self, cart_id: UUID) -> Optional[MstCart]:
        return await self.cart_repo.get_cart_by_id(cart_id)