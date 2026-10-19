"""Tests for user-related endpoints: GET /users/{id}."""
from tests.conftest import register_user


# ── 19. GET /users/{id} returns the user; unknown id returns 404 ─────────

def test_get_user_by_id(client):
    # Register a user, then look them up by id.
    created = register_user(client, email="lookup@example.com").json()
    user_id = created["id"]

    resp = client.get(f"/users/{user_id}")
    assert resp.status_code == 200
    assert resp.json()["email"] == "lookup@example.com"


def test_get_unknown_user_returns_404(client):
    # A non-existent user id should give 404.
    resp = client.get("/users/999999")
    assert resp.status_code == 404
