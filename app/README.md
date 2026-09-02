# Todo API

A minimal REST API for managing a to-do list, built with FastAPI and SQLite. No authentication, no external services — just a single SQLite file and a running Python process.

---

## How to run locally

```bash
# 1. Install dependencies (from the app/ directory)
pip install -r requirements.txt

# 2. Start the server (from the project root, one level above app/)
uvicorn app.main:app --reload

# 3. Verify it's running
curl http://127.0.0.1:8000/todos
```

Interactive API docs (Swagger UI) are available at <http://127.0.0.1:8000/docs> while the server is running.

The SQLite database file (`app/todos.db`) is created automatically on first startup.

---

## Running tests

```bash
# From the project root
pytest app/test_main.py -v
```

Tests use an isolated throwaway database — they never touch `todos.db`.

---

## Endpoints

### `POST /todos` — Create a todo

```bash
curl -X POST http://127.0.0.1:8000/todos \
  -H "Content-Type: application/json" \
  -d '{"title": "Buy milk"}'
```

**Request body:** `{ "title": string }` — required, non-empty, max 200 characters.

**Response `201`:**
```json
{ "id": 1, "title": "Buy milk", "done": false }
```

---

### `GET /todos` — List all todos

```bash
curl http://127.0.0.1:8000/todos
```

**Response `200`:**
```json
[
  { "id": 1, "title": "Buy milk", "done": false },
  { "id": 2, "title": "Read docs", "done": true }
]
```

---

### `GET /todos/{id}` — Get a single todo

```bash
curl http://127.0.0.1:8000/todos/1
```

**Response `200`:** the todo object, or `404` if the id does not exist.

---

### `PUT /todos/{id}` — Update a todo

Both fields are optional. Supply one or both.

```bash
# Mark done
curl -X PUT http://127.0.0.1:8000/todos/1 \
  -H "Content-Type: application/json" \
  -d '{"done": true}'

# Rename and mark done in one request
curl -X PUT http://127.0.0.1:8000/todos/1 \
  -H "Content-Type: application/json" \
  -d '{"title": "Buy oat milk", "done": true}'
```

**Request body:** `{ "title"?: string, "done"?: boolean }` — both optional; if `title` is supplied, same constraints apply (non-empty, max 200 chars).

**Response `200`:** the updated todo object, or `404` if the id does not exist.

---

### `DELETE /todos/{id}` — Delete a todo

```bash
curl -X DELETE http://127.0.0.1:8000/todos/1
```

**Response `204`** (no body), or `404` if the id does not exist.

---

### `PATCH /todos/{id}/toggle` — Toggle completion status

Flips `done` from `false` to `true` or `true` to `false`.

```bash
curl -X PATCH http://127.0.0.1:8000/todos/1/toggle
```

**Response `200`:** the updated todo object with `done` flipped, or `404` if the id does not exist.

---

## Todo object shape

```json
{
  "id": 1,
  "title": "Buy milk",
  "done": false
}
```

| Field | Type | Notes |
|---|---|---|
| `id` | integer | Auto-assigned on creation |
| `title` | string | Non-empty, max 200 characters |
| `done` | boolean | Defaults to `false` on creation |

---

## Error responses

| Status | When | Body |
|---|---|---|
| `404` | `id` not found on any `GET`, `PUT`, `DELETE`, or `PATCH` | `{"detail": "todo not found"}` |
| `422` | Malformed request body (missing `title`, empty string, title over 200 chars, non-boolean `done`) | FastAPI default validation error |
