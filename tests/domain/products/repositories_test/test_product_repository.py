import pytest
import uuid

from app.domain.products.repositories import ProductRepository


@pytest.mark.asyncio
async def test_create_and_fetch_product(db_session):
    repo = ProductRepository(db_session)
    product = await repo.create_product(
        name="Phone",
        description="Smartphone",
        price=500,
        stock=15,
        product_image_url=None,
    )

    fetched = await repo.get_product_by_id(product.id_product)

    assert fetched is not None
    assert fetched.name == "Phone"
    assert getattr(fetched, "stock", None) == 15


@pytest.mark.asyncio
async def test_update_product_and_stock(db_session):
    repo = ProductRepository(db_session)
    product = await repo.create_product(
        name="Laptop",
        description="",
        price=1000,
        stock=3,
        product_image_url=None,
    )

    updated = await repo.update_product(
        product.id_product,
        name="Gaming Laptop",
        description="RTX",
        price=1500,
        product_image_url="/img.png",
    )
    assert updated is not None
    assert updated.name == "Gaming Laptop"
    assert updated.price == 1500

    stock = await repo.update_product_stock(product.id_product, 8)
    assert stock is not None
    assert stock.stock == 8


@pytest.mark.asyncio
async def test_get_all_and_delete_product(db_session):
    repo = ProductRepository(db_session)
    await repo.create_product(name="A", description=None, price=10, stock=1, product_image_url=None)
    await repo.create_product(name="B", description=None, price=20, stock=2, product_image_url=None)

    products = await repo.get_all_products(limit=10, offset=0)
    assert len(products) == 2

    delete_result = await repo.delete_product(products[0].id_product)
    assert delete_result is True

    remaining = await repo.get_all_products(limit=10, offset=0)
    assert len(remaining) == 1
