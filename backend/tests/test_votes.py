"""Tests for the voting system: PUT /api/snippets/{id}/vote, DELETE …/vote."""
from tests.conftest import create_snippet, get_auth_headers


# ── 14. Voting requires a token ──────────────────────────────────────────

def test_vote_requires_auth(client, auth_headers):
    # Create a snippet (needs auth), then try to vote without a token.
    snip_id = create_snippet(client, auth_headers).json()["id"]
    resp = client.put(f"/api/snippets/{snip_id}/vote", json={"value": 1})
    assert resp.status_code == 401


# ── 15. Voting twice with the same value does NOT double-count ───────────

def test_duplicate_vote_same_value(client, auth_headers):
    # Upvote the same snippet twice — score should stay at 1, not 2.
    snip_id = create_snippet(client, auth_headers).json()["id"]

    client.put(f"/api/snippets/{snip_id}/vote", json={"value": 1}, headers=auth_headers)
    resp = client.put(
        f"/api/snippets/{snip_id}/vote", json={"value": 1}, headers=auth_headers
    )

    assert resp.json()["vote_count"] == 1


# ── 16. Changing a vote replaces the old value ───────────────────────────

def test_change_vote_replaces_value(client, auth_headers):
    # Upvote, then switch to downvote — net score should be -1.
    snip_id = create_snippet(client, auth_headers).json()["id"]

    client.put(f"/api/snippets/{snip_id}/vote", json={"value": 1}, headers=auth_headers)
    resp = client.put(
        f"/api/snippets/{snip_id}/vote", json={"value": -1}, headers=auth_headers
    )

    assert resp.json()["vote_count"] == -1


# ── 17. Two different users' votes add up ────────────────────────────────

def test_two_users_votes_add_up(client, auth_headers, second_auth_headers):
    # Both users upvote → vote_count should be 2.
    snip_id = create_snippet(client, auth_headers).json()["id"]

    client.put(f"/api/snippets/{snip_id}/vote", json={"value": 1}, headers=auth_headers)
    resp = client.put(
        f"/api/snippets/{snip_id}/vote", json={"value": 1}, headers=second_auth_headers
    )

    assert resp.json()["vote_count"] == 2


# ── 18. DELETE vote removes the vote; /users/me/votes reflects it ────────

def test_delete_vote_updates_score_and_my_votes(client, auth_headers):
    # Create, upvote, then remove the vote.
    snip_id = create_snippet(client, auth_headers).json()["id"]

    # Upvote.
    client.put(f"/api/snippets/{snip_id}/vote", json={"value": 1}, headers=auth_headers)

    # Confirm it appears in /users/me/votes.
    votes_before = client.get("/users/me/votes", headers=auth_headers).json()
    assert any(v["snip_id"] == snip_id for v in votes_before)

    # Delete the vote.
    resp = client.delete(f"/api/snippets/{snip_id}/vote", headers=auth_headers)
    assert resp.json()["vote_count"] == 0

    # /users/me/votes should no longer list it.
    votes_after = client.get("/users/me/votes", headers=auth_headers).json()
    assert not any(v["snip_id"] == snip_id for v in votes_after)
