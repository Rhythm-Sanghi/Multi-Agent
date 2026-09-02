# Design Brief — To-Do REST API

## Summary
A FastAPI-based REST API backed by a single SQLite file that exposes five CRUD endpoints plus a toggle action for managing to-do items. No auth, no frontend, no external services.

---

## Data Model

### Table: `todos`

| Field   | Type      | Constraints                        |
|---------|-----------|------------------------------------|
| `id`    | `INTEGER` | Primary key, auto-increment        |
| `title` | `TEXT`    | Not null, non-empty string, max 200 characters |
| `done`  | `INTEGER` | Not null, default `0` (SQLite has no native BOOLEAN; store as `0`/`1`) |

### Pydantic schemas (request/response)

| Schema           | Fields                                    | Notes                                                  | Used by              |
|------------------|-------------------------------------------|--------------------------------------------------------|----------------------|
| `TodoCreate`     | `title: str`                              | Must be non-empty and ≤ 200 characters; Pydantic raises `422` if violated | `POST /todos` |
| `TodoUpdate`     | `title: Optional[str]`, `done: Optional[bool]` | If `title` is supplied, same constraints apply: non-empty and ≤ 200 characters | `PUT /todos/{id}` |
| `TodoResponse`   | `id: int`, `title: str`, `done: bool`     | `done` is read from the DB as `INTEGER` `0`/`1` and converted to `bool` by this schema | All responses |

---

## Endpoints / Interfaces

| Method   | Path           | Request Body                              | Success Response                        | Error Response            |
|----------|----------------|-------------------------------------------|-----------------------------------------|---------------------------|
| `POST`   | `/todos`       | `{"title": string}`                       | `201` + `TodoResponse`                  | `422` (malformed body)    |
| `GET`    | `/todos`       | —                                         | `200` + `TodoResponse[]`                | —                         |
| `GET`    | `/todos/{id}`  | —                                         | `200` + `TodoResponse`                  | `404` `{"detail": "todo not found"}` |
| `PUT`    | `/todos/{id}`  | `{"title"?: string, "done"?: bool}`       | `200` + `TodoResponse`                  | `404` `{"detail": "todo not found"}` |
| `DELETE` | `/todos/{id}`        | —                                         | `204` (no body)                         | `404` `{"detail": "todo not found"}` |
| `PATCH`  | `/todos/{id}/toggle` | —                                         | `200` + `TodoResponse` with `done` flipped | `404` `{"detail": "todo not found"}` |

---

## Libraries / Dependencies

| Library          | Justification                                                        |
|------------------|----------------------------------------------------------------------|
| `fastapi`        | Framework specified in scope                                         |
| `uvicorn`        | Standard ASGI server for running FastAPI locally                     |
| `sqlite3`        | Python stdlib module; no install needed. Used directly for all DB access — no ORM, no query builder. |
| `pydantic`       | Bundled with FastAPI; used for request/response schema validation     |

No additional libraries are needed. Do **not** add `sqlalchemy`, `alembic`, `databases`, `asyncpg`, or any other ORM, migration tool, or DB layer.

---

## Edge Cases and Error Conditions

| Condition                                        | Expected Behavior                                        |
|--------------------------------------------------|----------------------------------------------------------|
| `POST` with missing or empty `title`             | Pydantic returns `422` — no custom handling needed |
| `POST` with `title` longer than 200 characters   | Pydantic returns `422` — no custom handling needed |
| `PUT` with `title` longer than 200 characters    | Pydantic returns `422` — no custom handling needed |
| `GET /todos/{id}` with non-existent id           | Return `404` with `{"detail": "todo not found"}`        |
| `PUT /todos/{id}` with non-existent id           | Return `404` with `{"detail": "todo not found"}`        |
| `PUT /todos/{id}` with neither `title` nor `done` supplied | No fields change; return `200` with unchanged todo (no-op update is acceptable) |
| `DELETE /todos/{id}` with non-existent id        | Return `404` with `{"detail": "todo not found"}`        |
| `PATCH /todos/{id}/toggle` with non-existent id  | Return `404` with `{"detail": "todo not found"}`        |
| `PUT` with `done` supplied as a non-boolean      | FastAPI/Pydantic returns `422` — no custom handling needed |
| `id` path parameter is not an integer            | FastAPI returns `422` automatically — no custom handling needed |
| SQLite file does not exist on first run          | A startup function calls `sqlite3.connect(DB_PATH)` and runs `CREATE TABLE IF NOT EXISTS todos (...)` — file and table are created automatically |

---

## Explicitly Out of Scope

The following are **forbidden** for this implementation. Do not add them even if they seem trivial:

- Authentication or user accounts
- Multi-user support / multi-tenancy
- Pagination, filtering, sorting, or search on `GET /todos`
- Frontend UI of any kind
- Postgres, MySQL, or any external database service
- Docker / Docker Compose / containerization
- Deployment or hosting configuration
- Rate limiting, logging middleware, or observability tooling
- Input validation beyond: `title` is a non-empty string of ≤ 200 characters, and `done` is a boolean
- Custom `422` error messages (FastAPI default is sufficient)
