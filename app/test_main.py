import pytest
from fastapi.testclient import TestClient

import app.main as main_module
from app.main import app, _init_db


@pytest.fixture()
def client(tmp_path, monkeypatch):
    """Return a TestClient backed by a fresh throwaway SQLite database."""
    test_db = str(tmp_path / "test_todos.db")
    monkeypatch.setattr(main_module, "DB_PATH", test_db)
    _init_db(test_db)
    with TestClient(app) as c:
        yield c


# ---------------------------------------------------------------------------
# POST /todos — happy path
# ---------------------------------------------------------------------------

def test_create_todo(client):
    resp = client.post("/todos", json={"title": "Buy milk"})
    assert resp.status_code == 201
    data = resp.json()
    assert data["title"] == "Buy milk"
    assert data["done"] is False
    assert isinstance(data["id"], int)


def test_create_todo_title_too_long(client):
    resp = client.post("/todos", json={"title": "x" * 201})
    assert resp.status_code == 422


# ---------------------------------------------------------------------------
# GET /todos — happy path
# ---------------------------------------------------------------------------

def test_list_todos(client):
    client.post("/todos", json={"title": "Task A"})
    resp = client.get("/todos")
    assert resp.status_code == 200
    items = resp.json()
    assert len(items) == 1
    assert items[0]["title"] == "Task A"


# ---------------------------------------------------------------------------
# GET /todos/{id} — happy path + 404
# ---------------------------------------------------------------------------

def test_get_todo(client):
    created = client.post("/todos", json={"title": "Read docs"}).json()
    resp = client.get(f"/todos/{created['id']}")
    assert resp.status_code == 200
    assert resp.json()["title"] == "Read docs"


def test_get_todo_not_found(client):
    resp = client.get("/todos/9999")
    assert resp.status_code == 404
    assert resp.json() == {"detail": "todo not found"}


# ---------------------------------------------------------------------------
# PUT /todos/{id} — happy path + 404
# ---------------------------------------------------------------------------

def test_update_todo(client):
    created = client.post("/todos", json={"title": "Old title"}).json()
    resp = client.put(f"/todos/{created['id']}", json={"title": "New title", "done": True})
    assert resp.status_code == 200
    data = resp.json()
    assert data["title"] == "New title"
    assert data["done"] is True


def test_update_todo_not_found(client):
    resp = client.put("/todos/9999", json={"title": "x"})
    assert resp.status_code == 404
    assert resp.json() == {"detail": "todo not found"}


def test_update_todo_title_too_long(client):
    created = client.post("/todos", json={"title": "Valid title"}).json()
    resp = client.put(f"/todos/{created['id']}", json={"title": "x" * 201})
    assert resp.status_code == 422


# ---------------------------------------------------------------------------
# DELETE /todos/{id} — happy path + 404
# ---------------------------------------------------------------------------

def test_delete_todo(client):
    created = client.post("/todos", json={"title": "To delete"}).json()
    resp = client.delete(f"/todos/{created['id']}")
    assert resp.status_code == 204


def test_delete_todo_not_found(client):
    resp = client.delete("/todos/9999")
    assert resp.status_code == 404
    assert resp.json() == {"detail": "todo not found"}


# ---------------------------------------------------------------------------
# PATCH /todos/{id}/toggle — happy path + 404
# ---------------------------------------------------------------------------

def test_toggle_todo(client):
    created = client.post("/todos", json={"title": "Toggle me"}).json()
    assert created["done"] is False
    resp = client.patch(f"/todos/{created['id']}/toggle")
    assert resp.status_code == 200
    assert resp.json()["done"] is True
    # toggle back
    resp2 = client.patch(f"/todos/{created['id']}/toggle")
    assert resp2.status_code == 200
    assert resp2.json()["done"] is False


def test_toggle_todo_not_found(client):
    resp = client.patch("/todos/9999/toggle")
    assert resp.status_code == 404
    assert resp.json() == {"detail": "todo not found"}


# ---------------------------------------------------------------------------
# Smoke test: GET /todos returns item just created by POST
# ---------------------------------------------------------------------------

def test_post_then_list_returns_item(client):
    client.post("/todos", json={"title": "Smoke test item"})
    items = client.get("/todos").json()
    assert any(i["title"] == "Smoke test item" for i in items)
