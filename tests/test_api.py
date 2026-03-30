def test_create_card(client):
    resp = client.post("/api/cards", data={
        "column_id": 1,
        "title": "New feature card",
        "description": "As a user, I want a feature",
    })
    assert resp.status_code == 200
    assert "New feature card" in resp.text


def test_update_card(client, seed_card):
    resp = client.post(f"/api/cards/{seed_card['id']}/update", data={
        "title": "Updated title",
        "description": "Updated desc",
    })
    assert resp.status_code == 200
    assert "Updated title" in resp.text


def test_delete_card(client):
    from app.repositories.cards import create_card
    card = create_card(column_id=1, title="To delete")
    resp = client.delete(f"/api/cards/{card['id']}")
    assert resp.status_code == 200
    assert "To delete" not in resp.text


def test_move_card(client, seed_card):
    resp = client.post(
        f"/api/cards/{seed_card['id']}/move",
        json={"column_id": 3, "position": 0},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["ok"] is True
    assert data["card"]["column_id"] == 3


def test_get_card_modal(client, seed_card):
    resp = client.get(f"/api/cards/{seed_card['id']}")
    assert resp.status_code == 200
    assert "Edit Card" in resp.text
    assert seed_card["title"] in resp.text


def test_move_card_missing(client):
    resp = client.post(
        "/api/cards/99999/move",
        json={"column_id": 1, "position": 0},
    )
    assert resp.status_code == 404
