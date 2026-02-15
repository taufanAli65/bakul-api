import pytest

from app.domain.carts.repositories import CartRepository
from tests.factories import create_product


@pytest.mark.asyncio
async def test_create_and_get_carts(db_session, user_factory):
    user = await user_factory()
    product = await create_product(db_session, price=50, stock=10)
    repo = CartRepository(db_session)

    cart = await repo.create_cart(user.id_user, product.id_product, quantity=2, price_at_time=100)
    carts = await repo.get_carts_by_user_id(user.id_user, limit=5, offset=0)

    assert cart in carts
    assert carts[0].price_at_time == 100


@pytest.mark.asyncio
async def test_update_and_delete_cart_item(db_session, user_factory):
    user = await user_factory()
    product = await create_product(db_session, price=20, stock=5)
    repo = CartRepository(db_session)

    cart = await repo.create_cart(user.id_user, product.id_product, quantity=1, price_at_time=20)

    updated = await repo.update_cart(cart.id_cart, quantity=3, price_at_time=60)
    assert updated is not None
    assert updated.quantity == 3
    assert updated.price_at_time == 60

    deleted = await repo.delete_cart_each_item(user.id_user, product.id_product)
    assert deleted is True


@pytest.mark.asyncio
async def test_empty_cart_by_user(db_session, user_factory):
    user = await user_factory()
    product1 = await create_product(db_session, price=10, stock=5)
    product2 = await create_product(db_session, price=15, stock=5)
    repo = CartRepository(db_session)

    await repo.create_cart(user.id_user, product1.id_product, quantity=1, price_at_time=10)
    await repo.create_cart(user.id_user, product2.id_product, quantity=2, price_at_time=30)

    result = await repo.empty_cart_by_user_id(user.id_user)
    assert result is True

    carts_after = await repo.get_carts_by_user_id(user.id_user)
    assert carts_after == []
