from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Response, status

import app.database as _db
from app.schemas import TodoCreate, TodoOut, TodoUpdate


@asynccontextmanager
async def lifespan(app: FastAPI):
    _db.init_db()
    yield


def get_db():
    return _db.get_db(_db.DB_PATH)


app = FastAPI(title="Todo API", lifespan=lifespan)


# ---------------------------------------------------------------------------
# POST /todos
# ---------------------------------------------------------------------------
@app.post("/todos", response_model=TodoOut, status_code=status.HTTP_201_CREATED)
def create_todo(payload: TodoCreate):
    conn = get_db()
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
    conn = get_db()
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
    conn = get_db()
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
    fields = {}
    if payload.title is not None:
        fields["title"] = payload.title
    if payload.done is not None:
        fields["done"] = int(payload.done)

    if not fields:
        # Nothing to update — just return the current state (or 404)
        return get_todo(id)

    set_clause = ", ".join(f"{col} = ?" for col in fields)
    values = list(fields.values()) + [id]

    conn = get_db()
    try:
        conn.execute(f"UPDATE todos SET {set_clause} WHERE id = ?", values)
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
# DELETE /todos/{id}
# ---------------------------------------------------------------------------
@app.delete("/todos/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_todo(id: int):
    conn = get_db()
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
