import pytest


@pytest.mark.asyncio
async def test_expedition_crud_flow(client):
    create_resp = await client.post("/api/v1/expeditions/", params={"name": "Courier"})
    assert create_resp.status_code == 201
    expedition_id = create_resp.json()["data"]["id"]

    list_resp = await client.get("/api/v1/expeditions", params={"limit": 10, "offset": 0})
    assert list_resp.status_code == 200

    detail_resp = await client.get(f"/api/v1/expeditions/{expedition_id}")
    assert detail_resp.status_code == 200

    update_resp = await client.put(f"/api/v1/expeditions/{expedition_id}", params={"name": "CourierX"})
    assert update_resp.status_code == 200
    assert update_resp.json()["data"]["name"] == "CourierX"

    delete_resp = await client.delete(f"/api/v1/expeditions/{expedition_id}")
    assert delete_resp.status_code == 200
