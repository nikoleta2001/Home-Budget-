from datetime import datetime

def auth_token(client):
    r = client.post("/auth/register", json={"email": "ex@example.com", "password": "secret123"})
    assert r.status_code == 201
    return r.json()["access_token"]

def auth_headers(token): 
    return {"Authorization": f"Bearer {token}"}

def test_expenses_and_analytics(client):
    token = auth_token(client)

    r1 = client.post("/categories", json={"name": "food"}, headers=auth_headers(token))
    assert r1.status_code == 201
    cat_food = r1.json()["id"]

    r2 = client.post("/categories", json={"name": "car"}, headers=auth_headers(token))
    assert r2.status_code == 201
    cat_car = r2.json()["id"]

    e1 = client.post("/expenses", json={"description":"pizza","amount":50,"category_id":cat_food}, headers=auth_headers(token))
    assert e1.status_code == 201
    e2 = client.post("/expenses", json={"description":"fuel","amount":30,"category_id":cat_car}, headers=auth_headers(token))
    assert e2.status_code == 201

    lst = client.get("/expenses", headers=auth_headers(token))
    assert lst.status_code == 200
    assert len(lst.json()) >= 2

    lst_food = client.get(f"/expenses?category_id={cat_food}", headers=auth_headers(token))
    assert lst_food.status_code == 200
    assert all(i.get("category", {}).get("name") == "food" for i in lst_food.json() if i.get("category"))

    an = client.get("/analytics/summary?period=this_month", headers=auth_headers(token))
    assert an.status_code == 200
    data = an.json()
    assert data["totals"]["spent"] >= 80.0
    cats = {row["category"]: row["total"] for row in data["by_category"]}
    assert cats.get("food") >= 50.0
    assert cats.get("car") >= 30.0
