import pytest

from app.domain.transactions.models import TransactionStatus
from app.domain.transactions.repositories import TransactionRepository
from tests.factories import create_expedition_service, create_product


@pytest.mark.asyncio
async def test_create_transaction_and_get(db_session, user_factory):
    user = await user_factory()
    expedition = await create_expedition_service(db_session, name="Ship")
    product = await create_product(db_session, price=40, stock=5)

    repo = TransactionRepository(db_session)
    transaction = await repo.create_transaction(
        id_user=user.id_user,
        id_expedition_service=expedition.id_expedition_service,
        items=[{"id_product": product.id_product, "quantity": 2, "price_at_time": 40}],
    )

    assert transaction.total == 80
    assert getattr(transaction, "status", None) == TransactionStatus.PENDING
    assert len(getattr(transaction, "items", [])) == 1

    fetched = await repo.get_transaction_by_id(transaction.id_transaction)
    assert fetched is not None
    assert fetched.id_transaction == transaction.id_transaction
    assert getattr(fetched, "status", None) == TransactionStatus.PENDING


@pytest.mark.asyncio
async def test_update_status_and_query_all(db_session, user_factory):
    user = await user_factory()
    expedition = await create_expedition_service(db_session, name="Express")
    product = await create_product(db_session, price=25, stock=5)

    repo = TransactionRepository(db_session)
    tx = await repo.create_transaction(
        id_user=user.id_user,
        id_expedition_service=expedition.id_expedition_service,
        items=[{"id_product": product.id_product, "quantity": 1, "price_at_time": 25}],
    )

    status = await repo.update_transaction_status(tx.id_transaction, TransactionStatus.PAID)
    assert status is not None
    assert status.status == TransactionStatus.PAID

    all_for_user = await repo.get_all_transactions(user_id=user.id_user, status=TransactionStatus.PAID, limit=10, offset=0)
    assert len(all_for_user) == 1
    assert getattr(all_for_user[0], "status", None) == TransactionStatus.PAID
