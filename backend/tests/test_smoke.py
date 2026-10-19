def test_snippets_list_starts_empty(client):
    response = client.get("/api/snippets/")
    assert response.status_code == 200
    assert response.json() == {"items": [], "total": 0}