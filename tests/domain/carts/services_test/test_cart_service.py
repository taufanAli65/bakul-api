import pytest

from app.domain.carts.repositories import CartRepository
from app.domain.carts.schemas import CartCreate, CartUpdate
from app.domain.carts.services import CartService
from tests.factories import create_product


@pytest.mark.asyncio
async def test_cart_service_create_and_update(db_session, user_factory):
    user = await user_factory()
    product = await create_product(db_session, price=15, stock=10)
    repo = CartRepository(db_session)
    service = CartService(repo)

    cart = await service.create_cart(
        CartCreate(id_user=user.id_user, id_product=product.id_product, quantity=2, price_at_time=30)
    )
    assert cart.quantity == 2

    updated = await service.update_cart(cart.id_cart, CartUpdate(quantity=4, price_at_time=60))
    assert updated is not None
    assert updated.quantity == 4


@pytest.mark.asyncio
async def test_empty_cart_via_service(db_session, user_factory):
    user = await user_factory()
    product = await create_product(db_session, price=12, stock=5)
    repo = CartRepository(db_session)
    service = CartService(repo)

    await service.create_cart(
        CartCreate(id_user=user.id_user, id_product=product.id_product, quantity=1, price_at_time=12)
    )

    emptied = await service.empty_cart_by_user_id(user.id_user)
    assert emptied is True
