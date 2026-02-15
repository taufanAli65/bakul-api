import uuid
from typing import Optional, Sequence
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.carts.repositories import CartRepository
from app.domain.expeditions.repositories import ExpeditionRepository
from app.domain.products.repositories import ProductRepository
from app.domain.transactions.repositories import TransactionItemData, TransactionRepository
from app.domain.transactions.models import MstTransaction


async def create_product(
    session: AsyncSession,
    *,
    name: Optional[str] = None,
    description: Optional[str] = "desc",
    price: int = 100,
    stock: int = 5,
    product_image_url: Optional[str] = None,
):
    repo = ProductRepository(session)
    return await repo.create_product(
        name=name or f"product-{uuid.uuid4().hex[:6]}",
        description=description,
        price=price,
        stock=stock,
        product_image_url=product_image_url,
    )


async def create_expedition_service(session: AsyncSession, *, name: Optional[str] = None):
    repo = ExpeditionRepository(session)
    return await repo.create_expedition_service(name or f"exp-{uuid.uuid4().hex[:6]}")


async def create_cart_item(
    session: AsyncSession,
    *,
    user_id,
    product_id,
    quantity: int = 1,
    price_at_time: int = 100,
):
    repo = CartRepository(session)
    return await repo.create_cart(user_id, product_id, quantity, price_at_time)


async def create_transaction(
    session: AsyncSession,
    *,
    user_id,
    expedition_service_id,
    items: Sequence[TransactionItemData],
) -> MstTransaction:
    repo = TransactionRepository(session)
    return await repo.create_transaction(
        id_user=user_id,
        id_expedition_service=expedition_service_id,
        items=items,
    )
