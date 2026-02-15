import pytest


@pytest.mark.asyncio
async def test_register_and_login(client):
    register_payload = {
        "email": "newuser@example.com",
        "password": "pass1234",
        "name": "New User",
        "role": "user",
        "profile_picture": None,
    }

    register_resp = await client.post("/api/v1/auth/register", json=register_payload)
    assert register_resp.status_code == 201
    body = register_resp.json()
    assert body["meta"]["success"] is True

    login_resp = await client.post(
        "/api/v1/auth/login", json={"email": "newuser@example.com", "password": "pass1234"}
    )
    assert login_resp.status_code == 200
    login_body = login_resp.json()
    assert login_body["data"]["access_token"]
