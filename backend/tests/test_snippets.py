"""Tests for snippet CRUD: create, read, update, delete, pagination, filters."""
import pytest

from tests.conftest import create_snippet, get_auth_headers


# ── 7. Creating a snippet without a token returns 401 ────────────────────

def test_create_snippet_requires_auth(client):
    # No Authorization header → 401.
    resp = client.post(
        "/api/snippets/",
        json={"title": "X", "language": "python", "code": "x=1"},
    )
    assert resp.status_code == 401


# ── 8. Creating a snippet with a token returns 201 and sets owner_id ─────

def test_create_snippet_sets_owner(client, auth_headers):
    # The snippet should belong to the authenticated user.
    resp = create_snippet(client, auth_headers)
    assert resp.status_code == 201

    body = resp.json()
    assert body["title"] == "Hello World"
    assert body["owner_id"] is not None

    # Verify owner_id matches the logged-in user.
    me = client.get("/users/me", headers=auth_headers).json()
    assert body["owner_id"] == me["id"]


# ── 9. A user cannot PATCH someone else's snippet (403) ──────────────────

def test_patch_other_users_snippet_forbidden(client, auth_headers, second_auth_headers):
    # Alice creates a snippet.
    snip_id = create_snippet(client, auth_headers).json()["id"]

    # Bob tries to patch it → 403.
    resp = client.patch(
        f"/api/snippets/{snip_id}",
        json={"title": "Hacked!"},
        headers=second_auth_headers,
    )
    assert resp.status_code == 403

    # Confirm the snippet is unchanged.
    original = client.get(f"/api/snippets/{snip_id}").json()
    assert original["title"] == "Hello World"


# ── 10. A user cannot DELETE someone else's snippet; owner can delete ────

def test_delete_permission_and_success(client, auth_headers, second_auth_headers):
    # Alice creates a snippet.
    snip_id = create_snippet(client, auth_headers).json()["id"]

    # Bob cannot delete it.
    resp = client.delete(f"/api/snippets/{snip_id}", headers=second_auth_headers)
    assert resp.status_code == 403

    # Alice (owner) deletes it.
    resp = client.delete(f"/api/snippets/{snip_id}", headers=auth_headers)
    assert resp.status_code == 204

    # A later GET should return 404.
    resp = client.get(f"/api/snippets/{snip_id}")
    assert resp.status_code == 404


# ── 11. Owner can PATCH their snippet, and updated_at gets set ───────────

def test_patch_own_snippet_changes_title(client, auth_headers):
    # Create a snippet, then patch the title.
    snip = create_snippet(client, auth_headers).json()

    resp = client.patch(
        f"/api/snippets/{snip['id']}",
        json={"title": "New Title"},
        headers=auth_headers,
    )
    assert resp.status_code == 200
    assert resp.json()["title"] == "New Title"


def test_patch_own_snippet_returns_updated_at(client, auth_headers):
    # The PATCH endpoint sets updated_at in the DB, and SnipPublic includes it.
    snip = create_snippet(client, auth_headers).json()

    resp = client.patch(
        f"/api/snippets/{snip['id']}",
        json={"title": "New Title"},
        headers=auth_headers,
    )
    body = resp.json()
    assert body["updated_at"] is not None


# ── 12. Pagination: default page and offset ──────────────────────────────

def test_pagination(client, auth_headers):
    # Create 12 snippets.
    for i in range(12):
        create_snippet(client, auth_headers, title=f"Snippet {i}")

    # Default page (limit=10) should return 10 items but total=12.
    resp = client.get("/api/snippets/")
    body = resp.json()
    assert len(body["items"]) == 10
    assert body["total"] == 12

    # offset=10 should return the remaining 2.
    resp2 = client.get("/api/snippets/?offset=10")
    body2 = resp2.json()
    assert len(body2["items"]) == 2
    assert body2["total"] == 12


# ── 13. Filters and sorting ──────────────────────────────────────────────

def test_language_filter(client, auth_headers):
    # Create snippets in different languages.
    create_snippet(client, auth_headers, title="Py1", language="python")
    create_snippet(client, auth_headers, title="JS1", language="javascript")
    create_snippet(client, auth_headers, title="Py2", language="python")

    resp = client.get("/api/snippets/?language=python")
    body = resp.json()
    assert body["total"] == 2
    assert all(s["language"] == "python" for s in body["items"])


def test_case_insensitive_search(client, auth_headers):
    # Search should be case-insensitive on title and description.
    create_snippet(client, auth_headers, title="My Awesome Func", description="cool")
    create_snippet(client, auth_headers, title="Boring", description="nothing")

    # Searching "awesome" (lowercase) should match the first snippet.
    resp = client.get("/api/snippets/?q=awesome")
    body = resp.json()
    assert body["total"] == 1
    assert "Awesome" in body["items"][0]["title"]


def test_sort_top_orders_by_vote_count(client, auth_headers, second_auth_headers):
    # Create two snippets with different vote counts.
    s1 = create_snippet(client, auth_headers, title="Low").json()["id"]
    s2 = create_snippet(client, auth_headers, title="High").json()["id"]

    # Upvote s2 twice (two different users).
    client.put(f"/api/snippets/{s2}/vote", json={"value": 1}, headers=auth_headers)
    client.put(f"/api/snippets/{s2}/vote", json={"value": 1}, headers=second_auth_headers)

    # sort=top should put "High" first.
    resp = client.get("/api/snippets/?sort=top")
    items = resp.json()["items"]
    assert items[0]["title"] == "High"
    assert items[0]["vote_count"] >= items[1]["vote_count"]
