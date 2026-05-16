import pytest

pytestmark = pytest.mark.asyncio

# POST /expenses
async def test_create_expense_returns_201_and_full_object(client):
    payload = {
        "amount": 450.00,
        "category": "food",
        "expense_date": "2025-04-05",
        "note": "lunch",
    }
    response = await client.post("/expenses", json=payload)

    assert response.status_code == 201
    body = response.json()
    assert body["amount"] == "450.00"
    assert body["category"] == "food"
    assert body["expense_date"] == "2025-04-05"
    assert body["note"] == "lunch"
    assert "id" in body
    assert "created_at" in body
    assert "updated_at" in body


async def test_create_expense_rejects_negative_amount(client):
    payload = {"amount": -10, "category": "food", "expense_date": "2025-04-05"}
    response = await client.post("/expenses", json=payload)
    assert response.status_code == 422


async def test_create_expense_rejects_zero_amount(client):
    payload = {"amount": 0, "category": "food", "expense_date": "2025-04-05"}
    response = await client.post("/expenses", json=payload)
    assert response.status_code == 422


async def test_create_expense_rejects_missing_category(client):
    payload = {"amount": 100, "expense_date": "2025-04-05"}
    response = await client.post("/expenses", json=payload)
    assert response.status_code == 422


async def test_create_expense_rejects_empty_category(client):
    payload = {"amount": 100, "category": "", "expense_date": "2025-04-05"}
    response = await client.post("/expenses", json=payload)
    assert response.status_code == 422


# GET /expenses
async def test_list_expenses_empty(client):
    response = await client.get("/expenses")
    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 0
    assert body["total_amount"] == "0"
    assert body["items"] == []


async def test_list_expenses_returns_all_and_totals(client):
    await client.post(
        "/expenses",
        json={"amount": 450, "category": "food", "expense_date": "2025-04-05"},
    )
    await client.post(
        "/expenses",
        json={"amount": 500, "category": "transport", "expense_date": "2025-04-06"},
    )

    response = await client.get("/expenses")
    body = response.json()
    assert response.status_code == 200
    assert body["total"] == 2
    assert body["total_amount"] == "950.00"
    assert len(body["items"]) == 2


async def test_list_expenses_filters_by_category(client):
    await client.post(
        "/expenses",
        json={"amount": 450, "category": "food", "expense_date": "2025-04-05"},
    )
    await client.post(
        "/expenses",
        json={"amount": 500, "category": "transport", "expense_date": "2025-04-06"},
    )

    response = await client.get("/expenses?category=food")
    body = response.json()
    assert response.status_code == 200
    assert body["total"] == 1
    assert body["items"][0]["category"] == "food"


async def test_list_expenses_filters_by_date_range(client):
    for amount, day in [(100, "01"), (200, "15"), (300, "28")]:
        await client.post(
            "/expenses",
            json={
                "amount": amount,
                "category": "food",
                "expense_date": f"2025-04-{day}",
            },
        )

    response = await client.get("/expenses?date_from=2025-04-10&date_to=2025-04-20")
    body = response.json()
    assert response.status_code == 200
    assert body["total"] == 1
    assert body["items"][0]["amount"] == "200.00"


async def test_list_expenses_pagination(client):
    for i in range(5):
        await client.post(
            "/expenses",
            json={"amount": 100 + i, "category": "food", "expense_date": "2025-04-05"},
        )

    response = await client.get("/expenses?skip=2&limit=2")
    body = response.json()
    assert response.status_code == 200
    assert body["total"] == 5
    assert len(body["items"]) == 2


# PUT /expenses/{id}
async def test_update_expense_changes_fields(client):
    created = await client.post(
        "/expenses",
        json={"amount": 450, "category": "food", "expense_date": "2025-04-05"},
    )
    expense_id = created.json()["id"]

    response = await client.put(
        f"/expenses/{expense_id}",
        json={"amount": 500, "category": "transport", "note": "correction"},
    )
    body = response.json()
    assert response.status_code == 200
    assert body["amount"] == "500.00"
    assert body["category"] == "transport"
    assert body["note"] == "correction"
    assert body["expense_date"] == "2025-04-05"  # unchanged


async def test_update_expense_partial(client):
    created = await client.post(
        "/expenses",
        json={"amount": 450, "category": "food", "expense_date": "2025-04-05"},
    )
    expense_id = created.json()["id"]

    response = await client.put(f"/expenses/{expense_id}", json={"note": "added later"})
    body = response.json()
    assert response.status_code == 200
    assert body["note"] == "added later"
    assert body["amount"] == "450.00"
    assert body["category"] == "food"


async def test_update_expense_returns_404_when_missing(client):
    fake_id = "00000000-0000-0000-0000-000000000000"
    response = await client.put(f"/expenses/{fake_id}", json={"amount": 100})
    assert response.status_code == 404
    assert response.json()["detail"] == "Expense not found"


async def test_update_expense_rejects_negative_amount(client):
    created = await client.post(
        "/expenses",
        json={"amount": 450, "category": "food", "expense_date": "2025-04-05"},
    )
    expense_id = created.json()["id"]

    response = await client.put(f"/expenses/{expense_id}", json={"amount": -50})
    assert response.status_code == 422


# DELETE /expenses/{id}
async def test_delete_expense_returns_204_and_removes(client):
    created = await client.post(
        "/expenses",
        json={"amount": 450, "category": "food", "expense_date": "2025-04-05"},
    )
    expense_id = created.json()["id"]

    response = await client.delete(f"/expenses/{expense_id}")
    assert response.status_code == 204
    assert response.content == b""

    list_response = await client.get("/expenses")
    assert list_response.json()["total"] == 0


async def test_delete_expense_returns_404_when_missing(client):
    fake_id = "00000000-0000-0000-0000-000000000000"
    response = await client.delete(f"/expenses/{fake_id}")
    assert response.status_code == 404


# /health
async def test_health_returns_ok(client):
    response = await client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["database"] == "ok"
