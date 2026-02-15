import pytest


@pytest.mark.asyncio
async def test_product_crud_flow(client):
    create_resp = await client.post(
        "/api/v1/products/",
        data={"name": "Widget", "price": "120", "stock": "5", "description": "Test widget"},
    )
    assert create_resp.status_code == 201
    product_id = create_resp.json()["data"]["id"]

    list_resp = await client.get("/api/v1/products", params={"limit": 10, "offset": 0})
    assert list_resp.status_code == 200
    assert any(p["id"] == product_id for p in list_resp.json()["data"])

    detail_resp = await client.get(f"/api/v1/products/{product_id}")
    assert detail_resp.status_code == 200

    update_resp = await client.put(
        f"/api/v1/products/{product_id}",
        json={"name": "Widget2", "description": "Updated", "price": 150, "product_image_url": None},
    )
    assert update_resp.status_code == 200
    assert update_resp.json()["data"]["name"] == "Widget2"

    stock_resp = await client.put(f"/api/v1/products/{product_id}/stock", params={"stock": 8})
    assert stock_resp.status_code == 200
    assert stock_resp.json()["data"]["stock"] == 8

    delete_resp = await client.delete(f"/api/v1/products/{product_id}")
    assert delete_resp.status_code == 200
