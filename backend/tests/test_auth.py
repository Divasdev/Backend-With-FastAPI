"""Tests for authentication: register, login, and /users/me."""
from tests.conftest import register_user, login_user, get_auth_headers


# ── 1. Register succeeds and response has no password fields ──────────────

def test_register_succeeds_and_hides_password(client):
    # Registration should return 201 and never expose password or hash.
    resp = register_user(client, email="new@example.com")
    assert resp.status_code == 201

    body = resp.json()
    assert body["email"] == "new@example.com"
    assert "id" in body
    assert "password" not in body
    assert "hashed_password" not in body


# ── 2. Duplicate email returns 400 (case-insensitive) ─────────────────────

def test_duplicate_email_rejected(client):
    # First registration succeeds.
    resp1 = register_user(client, email="dupe@example.com")
    assert resp1.status_code == 201

    # Exact same email → 400.
    resp2 = register_user(client, email="dupe@example.com")
    assert resp2.status_code == 400

    # Different letter case still counts as a duplicate.
    resp3 = register_user(client, email="DUPE@Example.com")
    assert resp3.status_code == 400


# ── 3. Password shorter than 8 chars is rejected (422) ───────────────────

def test_short_password_rejected(client):
    # The Form(min_length=8) constraint should trigger a 422.
    resp = register_user(client, email="short@example.com", password="abc")
    assert resp.status_code == 422


# ── 4. Login with correct credentials returns an access token ─────────────

def test_login_returns_token(client):
    # Register first, then log in.
    register_user(client, email="login@example.com")
    resp = login_user(client, email="login@example.com")
    assert resp.status_code == 200

    body = resp.json()
    assert "access_token" in body
    assert body["token_type"] == "bearer"
    assert len(body["access_token"]) > 0


# ── 5. Login with wrong password returns 401 ─────────────────────────────

def test_login_wrong_password(client):
    # Register, then try logging in with a bad password.
    register_user(client, email="wrong@example.com")
    resp = login_user(client, email="wrong@example.com", password="badpassword99")
    assert resp.status_code == 401


# ── 6. /users/me: 401 without token, 200 with valid token ────────────────

def test_users_me_requires_auth(client):
    # No token → 401.
    resp = client.get("/users/me")
    assert resp.status_code == 401


def test_users_me_returns_user(client):
    # With a valid token we get back the user's profile.
    headers = get_auth_headers(client, email="me@example.com")
    resp = client.get("/users/me", headers=headers)
    assert resp.status_code == 200

    body = resp.json()
    assert body["email"] == "me@example.com"
    assert "id" in body
    assert "hashed_password" not in body
