import pytest


@pytest.mark.asyncio
async def test_get_and_update_me(client, regular_user):
    resp = await client.get("/api/v1/users/me")
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["email"] == regular_user.email

    update_resp = await client.put(
        "/api/v1/users/me",
        json={"name": "Updated", "email": regular_user.email, "role": None, "profile_picture": None},
    )
    assert update_resp.status_code == 200
    assert update_resp.json()["data"]["name"] == "Updated"


@pytest.mark.asyncio
async def test_list_users_requires_admin(client, admin_user):
    resp = await client.get("/api/v1/users", params={"limit": 10, "offset": 0})
    assert resp.status_code == 200
    body = resp.json()
    assert body["meta"]["success"] is True
    assert len(body["data"]) >= 2
