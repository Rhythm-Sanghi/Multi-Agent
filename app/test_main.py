import pytest
from fastapi.testclient import TestClient

import app.database as db_module
from app.database import init_db
from app.main import app


@pytest.fixture()
def client(tmp_path, monkeypatch):
    """Return a TestClient backed by a fresh throwaway SQLite database."""
    test_db = str(tmp_path / "test_todos.db")
    monkeypatch.setattr(db_module, "DB_PATH", test_db)
    init_db(test_db)
    with TestClient(app) as c:
        yield c


# ---------------------------------------------------------------------------
# Tests — one per endpoint (happy path)
# ---------------------------------------------------------------------------

def test_create_todo(client):
    resp = client.post("/todos", json={"title": "Buy milk"})
    assert resp.status_code == 201
    data = resp.json()
    assert data["title"] == "Buy milk"
    assert data["done"] is False
    assert isinstance(data["id"], int)


def test_list_todos(client):
    client.post("/todos", json={"title": "Task A"})
    resp = client.get("/todos")
    assert resp.status_code == 200
    items = resp.json()
    assert len(items) == 1
    assert items[0]["title"] == "Task A"


def test_get_todo(client):
    created = client.post("/todos", json={"title": "Read docs"}).json()
    resp = client.get(f"/todos/{created['id']}")
    assert resp.status_code == 200
    assert resp.json()["title"] == "Read docs"


def test_update_todo(client):
    created = client.post("/todos", json={"title": "Old title"}).json()
    resp = client.put(f"/todos/{created['id']}", json={"title": "New title", "done": True})
    assert resp.status_code == 200
    data = resp.json()
    assert data["title"] == "New title"
    assert data["done"] is True


def test_delete_todo(client):
    created = client.post("/todos", json={"title": "To delete"}).json()
    resp = client.delete(f"/todos/{created['id']}")
    assert resp.status_code == 204
