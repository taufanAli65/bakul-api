import pytest

from app.domain.products.repositories import ProductRepository
from app.domain.products.schemas import ProductCreate, ProductUpdate
from app.domain.products.services import ProductService


@pytest.mark.asyncio
async def test_create_product_via_service(db_session):
    repo = ProductRepository(db_session)
    service = ProductService(repo)

    product = await service.create_product(
        ProductCreate(name="Camera", description="", price=200, stock=4, product_image_url=None)
    )

    assert product.name == "Camera"
    assert getattr(product, "stock", None) == 4


@pytest.mark.asyncio
async def test_update_and_delete_product(db_session):
    repo = ProductRepository(db_session)
    service = ProductService(repo)
    product = await service.create_product(
        ProductCreate(name="Mouse", description="", price=20, stock=10, product_image_url=None)
    )

    updated = await service.update_product(
        product.id_product,
        ProductUpdate(name="Wireless Mouse", description="BT", price=30, product_image_url="/mouse.png"),
    )
    assert updated is not None
    assert updated.name == "Wireless Mouse"
    assert updated.price == 30

    stock = await service.update_product_stock(product.id_product, 6)
    assert stock is not None
    assert stock.stock == 6

    deleted = await service.delete_product(product.id_product)
    assert deleted is True
