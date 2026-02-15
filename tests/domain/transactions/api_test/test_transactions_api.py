import pytest

from tests.factories import create_expedition_service, create_product


@pytest.mark.asyncio
async def test_transaction_endpoints_flow(client, db_session, regular_user):
    expedition = await create_expedition_service(db_session, name="Delivery")
    product = await create_product(db_session, price=60, stock=5)

    create_resp = await client.post(
        "/api/v1/transactions/",
        json={
            "id_expedition_service": str(expedition.id_expedition_service),
            "items": [
                {"id_product": str(product.id_product), "quantity": 2, "price_at_time": 120}
            ],
        },
    )
    assert create_resp.status_code == 201
    transaction_id = create_resp.json()["data"]["id"]

    list_resp = await client.get("/api/v1/transactions", params={"limit": 10, "offset": 0})
    assert list_resp.status_code == 200
    assert any(tx["id"] == transaction_id for tx in list_resp.json()["data"])

    detail_resp = await client.get(f"/api/v1/transactions/{transaction_id}")
    assert detail_resp.status_code == 200

    new_expedition = await create_expedition_service(db_session, name="DeliveryX")
    update_expedition_resp = await client.put(
        f"/api/v1/transactions/{transaction_id}/expedition",
        params={"expedition_service_id": str(new_expedition.id_expedition_service)},
    )
    assert update_expedition_resp.status_code == 200

    simulate_resp = await client.post(
        "/api/v1/transactions/simulation/payment",
        json={"transaction_id": transaction_id},
    )
    assert simulate_resp.status_code == 200

    status_resp = await client.put(
        f"/api/v1/transactions/{transaction_id}/status",
        json={"status": "shipped"},
    )
    assert status_resp.status_code == 200
