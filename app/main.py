import sqlite3
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException, Response, status
from pydantic import BaseModel, ConfigDict, Field, field_validator

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

DB_PATH = str(Path(__file__).parent / "todos.db")


# ---------------------------------------------------------------------------
# Pydantic schemas
# ---------------------------------------------------------------------------

class TodoCreate(BaseModel):
    title: str = Field(max_length=200)

    @field_validator("title")
    @classmethod
    def title_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("title must not be empty")
        return v


class TodoUpdate(BaseModel):
    title: Optional[str] = Field(default=None, max_length=200)
    done: Optional[bool] = None

    @field_validator("title")
    @classmethod
    def title_not_empty(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and not v.strip():
            raise ValueError("title must not be empty")
        return v


class TodoOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    done: bool


# ---------------------------------------------------------------------------
# Database helpers
# ---------------------------------------------------------------------------

def _init_db(path: str = DB_PATH) -> None:
    """Create the todos table if it does not already exist."""
    conn = sqlite3.connect(path)
    try:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS todos (
                id    INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT    NOT NULL,
                done  INTEGER NOT NULL DEFAULT 0
            )
            """
        )
        conn.commit()
    finally:
        conn.close()


def _get_conn() -> sqlite3.Connection:
    """Open and return a SQLite connection with row_factory set."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


# ---------------------------------------------------------------------------
# Application
# ---------------------------------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):
    _init_db(DB_PATH)
    yield


app = FastAPI(title="Todo API", lifespan=lifespan)


# ---------------------------------------------------------------------------
# POST /todos
# ---------------------------------------------------------------------------
@app.post("/todos", response_model=TodoOut, status_code=status.HTTP_201_CREATED)
def create_todo(payload: TodoCreate):
    conn = _get_conn()
    try:
        cursor = conn.execute(
            "INSERT INTO todos (title) VALUES (?)", (payload.title,)
        )
        conn.commit()
        row = conn.execute(
            "SELECT id, title, done FROM todos WHERE id = ?", (cursor.lastrowid,)
        ).fetchone()
    finally:
        conn.close()
    return dict(row)


# ---------------------------------------------------------------------------
# GET /todos
# ---------------------------------------------------------------------------
@app.get("/todos", response_model=list[TodoOut])
def list_todos():
    conn = _get_conn()
    try:
        rows = conn.execute("SELECT id, title, done FROM todos").fetchall()
    finally:
        conn.close()
    return [dict(r) for r in rows]


# ---------------------------------------------------------------------------
# GET /todos/{id}
# ---------------------------------------------------------------------------
@app.get("/todos/{id}", response_model=TodoOut)
def get_todo(id: int):
    conn = _get_conn()
    try:
        row = conn.execute(
            "SELECT id, title, done FROM todos WHERE id = ?", (id,)
        ).fetchone()
    finally:
        conn.close()
    if row is None:
        raise HTTPException(status_code=404, detail="todo not found")
    return dict(row)


# ---------------------------------------------------------------------------
# PUT /todos/{id}
# ---------------------------------------------------------------------------
@app.put("/todos/{id}", response_model=TodoOut)
def update_todo(id: int, payload: TodoUpdate):
    has_title = payload.title is not None
    has_done = payload.done is not None

    if not has_title and not has_done:
        # No-op update — return current state (or 404 if missing)
        return get_todo(id)

    conn = _get_conn()
    try:
        if has_title and has_done:
            conn.execute(
                "UPDATE todos SET title = ?, done = ? WHERE id = ?",
                (payload.title, int(payload.done), id),
            )
        elif has_title:
            conn.execute(
                "UPDATE todos SET title = ? WHERE id = ?",
                (payload.title, id),
            )
        else:
            conn.execute(
                "UPDATE todos SET done = ? WHERE id = ?",
                (int(payload.done), id),
            )
        conn.commit()
        row = conn.execute(
            "SELECT id, title, done FROM todos WHERE id = ?", (id,)
        ).fetchone()
    finally:
        conn.close()

    if row is None:
        raise HTTPException(status_code=404, detail="todo not found")
    return dict(row)


# ---------------------------------------------------------------------------
# PATCH /todos/{id}/toggle
# ---------------------------------------------------------------------------
@app.patch("/todos/{id}/toggle", response_model=TodoOut)
def toggle_todo(id: int):
    conn = _get_conn()
    try:
        row = conn.execute(
            "SELECT id, title, done FROM todos WHERE id = ?", (id,)
        ).fetchone()
        if row is None:
            raise HTTPException(status_code=404, detail="todo not found")
        new_done = 0 if row["done"] else 1
        conn.execute("UPDATE todos SET done = ? WHERE id = ?", (new_done, id))
        conn.commit()
        row = conn.execute(
            "SELECT id, title, done FROM todos WHERE id = ?", (id,)
        ).fetchone()
    finally:
        conn.close()
    return dict(row)


# ---------------------------------------------------------------------------
# DELETE /todos/{id}
# ---------------------------------------------------------------------------
@app.delete("/todos/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_todo(id: int):
    conn = _get_conn()
    try:
        row = conn.execute(
            "SELECT id FROM todos WHERE id = ?", (id,)
        ).fetchone()
        if row is None:
            raise HTTPException(status_code=404, detail="todo not found")
        conn.execute("DELETE FROM todos WHERE id = ?", (id,))
        conn.commit()
    finally:
        conn.close()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
