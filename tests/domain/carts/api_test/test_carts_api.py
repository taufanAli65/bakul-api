import pytest

from tests.factories import create_product


@pytest.mark.asyncio
async def test_cart_endpoints_flow(client, db_session, regular_user):
    product = await create_product(db_session, price=25, stock=10)

    create_resp = await client.post(
        "/api/v1/carts/",
        params={"product_id": str(product.id_product), "quantity": 2},
    )
    assert create_resp.status_code == 201
    cart_id = create_resp.json()["data"]["id"]

    list_resp = await client.get("/api/v1/carts", params={"limit": 10, "offset": 0})
    assert list_resp.status_code == 200
    assert any(item["id"] == cart_id for item in list_resp.json()["data"])

    update_resp = await client.put(f"/api/v1/carts/{cart_id}", params={"quantity": 3})
    assert update_resp.status_code == 200
    assert update_resp.json()["data"]["quantity"] == 3

    delete_resp = await client.delete("/api/v1/carts/item", params={"product_id": str(product.id_product)})
    assert delete_resp.status_code == 200

    empty_resp = await client.delete("/api/v1/carts/empty")
    assert empty_resp.status_code in (200, 404)
