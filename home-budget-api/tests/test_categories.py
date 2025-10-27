def get_token(client):
    r = client.post("/auth/register", json={"email": "cat@example.com", "password": "secret123"})
    assert r.status_code == 201
    return r.json()["access_token"]

def test_create_and_list_categories(client):
    token = get_token(client)

    r = client.post("/categories", json={"name": "food"}, headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 201, r.text
    assert r.json()["name"] == "food"

    r_dup = client.post("/categories", json={"name": "food"}, headers={"Authorization": f"Bearer {token}"})
    assert r_dup.status_code == 400

    r_list = client.get("/categories", headers={"Authorization": f"Bearer {token}"})
    assert r_list.status_code == 200
    items = r_list.json()
    assert isinstance(items, list)
    assert any(c["name"] == "food" for c in items)
