def test_register_and_login_flow(client):
    r = client.post("/auth/register", json={"email": "t1@example.com", "password": "secret123"})
    assert r.status_code == 201, r.text
    token = r.json()["access_token"]
    assert token

    r2 = client.post(
        "/auth/login",
        data={"username": "t1@example.com", "password": "secret123"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert r2.status_code == 200
    token2 = r2.json()["access_token"]
    assert token2
