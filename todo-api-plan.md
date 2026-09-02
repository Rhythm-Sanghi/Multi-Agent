# Plan: To-Do REST API (FastAPI + SQLite)

## Top-Level Overview

Build a minimal REST API for managing a to-do list, exactly as specified in `docs/scope.md`.
Five endpoints, SQLite storage, no auth, no frontend, no external services.
The implementation lives entirely inside the `app/` directory.

**Design decisions (confirmed with user):**
- All route handlers go in `app/main.py` (single-file, no separate `routes.py`)
- Tests use `pytest`'s `tmp_path` fixture for DB isolation — no manual teardown needed

---

## Sub-Tasks

---

### Sub-Task 1 — Project scaffold and dependencies

**Status:** [ ] pending

**Intent**  
Establish the Python package structure and declare dependencies so the app can be installed and run.

**Expected Outcomes**
- `app/requirements.txt` lists `fastapi`, `uvicorn[standard]`, and `pytest` (for tests)
- `app/__init__.py` exists (makes `app` a package, enables relative imports)
- `app/main.py` exists with a bare FastAPI app instance (no routes yet)
- Running `uvicorn app.main:app` starts without error

**Todo List**
1. Create `app/requirements.txt` with: `fastapi`, `uvicorn[standard]`, `pytest`, `httpx` (httpx is required by FastAPI's test client)
2. Create `app/__init__.py` (empty)
3. Create `app/main.py` — instantiate `FastAPI()`, import database helpers, no routes yet

**Relevant Context**
- `app/` is currently empty
- Stack is FastAPI + SQLite (stdlib `sqlite3`, no ORM)

---

### Sub-Task 2 — Database layer

**Status:** [ ] pending

**Intent**  
Create the SQLite database setup and a single helper that returns a connection. The DB file is created on first use.

**Expected Outcomes**
- `app/database.py` exists
- Calling `init_db()` creates the `todos` table if it does not already exist
- Columns: `id INTEGER PRIMARY KEY AUTOINCREMENT`, `title TEXT NOT NULL`, `done INTEGER NOT NULL DEFAULT 0`
- `get_db()` returns a configured `sqlite3.Connection` (row_factory = `sqlite3.Row`)
- `main.py` calls `init_db()` on startup (FastAPI lifespan or startup event)

**Todo List**
1. Create `app/database.py` with a `DB_PATH` constant (`app/todos.db`)
2. Implement `init_db(path=DB_PATH)` — accepts an optional path override (used by tests), creates `todos` table if not exists
3. Implement `get_db(path=DB_PATH)` — opens and returns a connection with `row_factory = sqlite3.Row`
4. Wire `init_db()` into `app/main.py` startup (FastAPI lifespan or `@app.on_event("startup")`)

**Relevant Context**
- Use stdlib `sqlite3` — no SQLAlchemy, no Alembic
- `done` is stored as INTEGER (0/1) and converted to bool at the schema layer
- DB file lives at `app/todos.db`; this path should be in `.gitignore`

---

### Sub-Task 3 — Pydantic schemas

**Status:** [ ] pending

**Intent**  
Define the request/response shapes FastAPI uses for validation and serialisation. Keeps route handlers thin.

**Expected Outcomes**
- `app/schemas.py` exists with three models:
  - `TodoCreate` — `title: str` (required, non-empty)
  - `TodoUpdate` — `title: str | None`, `done: bool | None` (both optional)
  - `TodoOut` — `id: int`, `title: str`, `done: bool`

**Todo List**
1. Create `app/schemas.py`
2. Define `TodoCreate(BaseModel)` — `title: str`, add a validator that rejects empty strings
3. Define `TodoUpdate(BaseModel)` — both fields optional, default `None`
4. Define `TodoOut(BaseModel)` — `id`, `title`, `done`; configure to read from ORM/dict attributes (`model_config = ConfigDict(from_attributes=True)` in Pydantic v2, or `orm_mode = True` in Pydantic v1)

**Relevant Context**
- Scope doc: "Input validation beyond 'title is a non-empty string' and 'done is a boolean'" is out of scope — so the only custom validator needed is the non-empty check on title
- FastAPI bundles Pydantic; use whatever Pydantic version ships with the installed FastAPI

---

### Sub-Task 4 — Route handlers (the 5 endpoints)

**Status:** [ ] pending

**Intent**  
Implement the five endpoints exactly as specified in the endpoint table in `docs/scope.md`.

**Expected Outcomes**  
All five endpoints work correctly:

| Method | Path | Success response |
|---|---|---|
| POST | /todos | 201, returns created todo |
| GET | /todos | 200, returns array |
| GET | /todos/{id} | 200 or 404 |
| PUT | /todos/{id} | 200 or 404 |
| DELETE | /todos/{id} | 204 or 404 |

- 404 body is `{"detail": "todo not found"}`
- `done` defaults to `false` on create
- PUT accepts either field independently (partial update)

**Todo List**
1. Add `POST /todos` handler to `app/main.py` — insert row, return `TodoOut` with status 201
2. Add `GET /todos` handler — select all rows, return list of `TodoOut`
3. Add `GET /todos/{id}` handler — select by id, 404 if missing
4. Add `PUT /todos/{id}` handler — build dynamic UPDATE from non-None fields, 404 if missing
5. Add `DELETE /todos/{id}` handler — delete by id, return 204, 404 if missing

**Relevant Context**
- Each handler opens a DB connection via `get_db()` and closes it when done (use a `try/finally` or context manager)
- Use `HTTPException(status_code=404, detail="todo not found")` for missing ids
- PUT partial update: only SET fields that are not `None` in the `TodoUpdate` payload
- All code lives in `app/main.py`; import schemas from `app/schemas.py` and DB helpers from `app/database.py`

---

### Sub-Task 5 — Tests

**Status:** [ ] pending

**Intent**  
Write one happy-path test per endpoint (five tests total) using FastAPI's `TestClient`. Satisfies the "Definition of done" requirement.

**Expected Outcomes**
- `app/test_main.py` exists
- Running `pytest app/test_main.py` passes with 5 tests (one per endpoint)
- Tests use an in-memory or temp-file SQLite DB, not the production `todos.db`

**Todo List**
1. Create `app/test_main.py`
2. Add a `pytest` fixture that uses `tmp_path` to create a throwaway SQLite file, patches `app.database.DB_PATH`, and calls `init_db()` on it; no manual teardown needed
3. Write `test_create_todo` — POST, assert 201 and returned fields
4. Write `test_list_todos` — POST one, then GET /todos, assert array contains it
5. Write `test_get_todo` — POST one, GET /todos/{id}, assert 200 and correct data
6. Write `test_update_todo` — POST one, PUT /todos/{id}, assert 200 and updated fields
7. Write `test_delete_todo` — POST one, DELETE /todos/{id}, assert 204

**Relevant Context**
- FastAPI `TestClient` requires `httpx` (already in requirements)
- Override the DB via a dependency override or by patching `DB_PATH` before `init_db()` runs
- Edge cases (404 paths) are not required by scope

---

### Sub-Task 6 — README

**Status:** [ ] pending

**Intent**  
Satisfy the "Definition of done" requirement: `app/README.md` must have a 3-line "how to run this locally" section.

**Expected Outcomes**
- `app/README.md` exists
- Contains exactly: install deps, run server, hit an endpoint — concise and accurate

**Todo List**
1. Create `app/README.md` with a short "How to run" section covering:
   - `pip install -r requirements.txt`
   - `uvicorn app.main:app --reload`
   - A sample `curl` command against `POST /todos`

**Relevant Context**
- Scope doc: "3-line 'how to run this locally' section"
- No Docker, no deployment config — just local dev instructions
