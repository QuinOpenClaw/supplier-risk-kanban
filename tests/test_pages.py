def test_board_loads(client):
    resp = client.get("/")
    assert resp.status_code == 200
    assert "Development" in resp.text
    assert "Backlog" in resp.text
    assert "In Progress" in resp.text
    assert "Done" in resp.text


def test_board_shows_card(client, seed_card):
    resp = client.get("/")
    assert resp.status_code == 200
    assert "Test user story" in resp.text


def test_board_404_for_missing(client):
    resp = client.get("/?board_id=999")
    assert resp.status_code == 404
