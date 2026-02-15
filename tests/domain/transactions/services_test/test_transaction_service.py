import pytest

from app.domain.carts.repositories import CartRepository
from app.domain.expeditions.repositories import ExpeditionRepository
from app.domain.products.repositories import ProductRepository
from app.domain.transactions.models import TransactionStatus
from app.domain.transactions.repositories import TransactionRepository
from app.domain.transactions.schemas import TransactionCreate, TransactionItem
from app.domain.transactions.services import TransactionService
from tests.factories import create_cart_item, create_expedition_service, create_product


@pytest.mark.asyncio
async def test_create_transaction_with_items(db_session, user_factory):
    user = await user_factory()
    expedition = await create_expedition_service(db_session, name="ShipFast")
    product_repo = ProductRepository(db_session)
    product = await product_repo.create_product(
        name="Keyboard", description="", price=50, stock=6, product_image_url=None
    )

    service = TransactionService(
        TransactionRepository(db_session),
        ExpeditionRepository(db_session),
        product_repo,
        CartRepository(db_session),
    )

    tx = await service.create_transaction(
        TransactionCreate(
            id_user=user.id_user,
            id_expedition_service=expedition.id_expedition_service,
            items=[TransactionItem(id_product=product.id_product, quantity=2, price_at_time=100)],
        )
    )

    assert tx.total == 200
    updated_product = await product_repo.get_product_by_id(product.id_product)
    assert getattr(updated_product, "stock", None) == 4


@pytest.mark.asyncio
async def test_create_transaction_from_cart(db_session, user_factory):
    user = await user_factory()
    expedition = await create_expedition_service(db_session, name="Snail")
    product = await create_product(db_session, price=30, stock=5)
    cart_repo = CartRepository(db_session)
    await cart_repo.create_cart(user.id_user, product.id_product, quantity=1, price_at_time=30)

    service = TransactionService(
        TransactionRepository(db_session),
        ExpeditionRepository(db_session),
        ProductRepository(db_session),
        cart_repo,
    )

    tx = await service.create_transaction(
        TransactionCreate(id_user=user.id_user, id_expedition_service=expedition.id_expedition_service, items=None)
    )

    assert getattr(tx, "items", [])
    emptied = await cart_repo.get_carts_by_user_id(user.id_user)
    assert emptied == []


@pytest.mark.asyncio
async def test_update_expedition_service_only_pending(db_session, user_factory):
    user = await user_factory()
    expedition1 = await create_expedition_service(db_session, name="First")
    expedition2 = await create_expedition_service(db_session, name="Second")
    product = await create_product(db_session, price=45, stock=4)

    transaction_repo = TransactionRepository(db_session)
    service = TransactionService(
        transaction_repo,
        ExpeditionRepository(db_session),
        ProductRepository(db_session),
        CartRepository(db_session),
    )

    tx = await service.create_transaction(
        TransactionCreate(
            id_user=user.id_user,
            id_expedition_service=expedition1.id_expedition_service,
            items=[TransactionItem(id_product=product.id_product, quantity=1, price_at_time=45)],
        )
    )

    updated = await service.update_expedition_service(tx.id_transaction, expedition2.id_expedition_service)
    assert updated is not None
    assert updated.id_expedition_service == expedition2.id_expedition_service

    await transaction_repo.update_transaction_status(tx.id_transaction, TransactionStatus.PAID)
    with pytest.raises(ValueError):
        await service.update_expedition_service(tx.id_transaction, expedition1.id_expedition_service)
