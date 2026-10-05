import pytest

from notes import create_app


@pytest.fixture
def client(tmp_path):
    app = create_app({"TESTING": True, "DATABASE": str(tmp_path / "test.sqlite3")})
    return app.test_client()


def test_create_get_and_list(client):
    r = client.post("/api/notes", json={"title": "Flask", "body": "blueprints", "tags": ["Python", "web"]})
    assert r.status_code == 201 and r.json["tags"] == ["python", "web"]
    assert client.get(f"/api/notes/{r.json['id']}").json["title"] == "Flask"
    assert len(client.get("/api/notes").json) == 1


def test_validation_errors(client):
    assert client.post("/api/notes", json={"title": "  "}).status_code == 400
    assert client.post("/api/notes", json={"title": "x", "tags": "notalist"}).status_code == 400


def test_search_and_tag_filter(client):
    client.post("/api/notes", json={"title": "RAG notes", "tags": ["ai"]})
    client.post("/api/notes", json={"title": "Groceries", "body": "milk", "tags": ["home"]})
    assert [n["title"] for n in client.get("/api/notes?q=milk").json] == ["Groceries"]
    assert [n["title"] for n in client.get("/api/notes?tag=ai").json] == ["RAG notes"]


def test_update_and_delete(client):
    nid = client.post("/api/notes", json={"title": "draft"}).json["id"]
    assert client.patch(f"/api/notes/{nid}", json={"title": "final"}).json["title"] == "final"
    assert client.delete(f"/api/notes/{nid}").status_code == 204
    assert client.get(f"/api/notes/{nid}").status_code == 404
