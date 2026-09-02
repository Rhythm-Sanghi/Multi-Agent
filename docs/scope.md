# Demo App Scope — To-Do REST API

**Status:** LOCKED. (v2 — amended to add PATCH /todos/{id}/toggle and title max-length validation, approved after review-agent flagged drift from design_brief.md)

---

## What we're building

A REST API for managing a to-do list. Nothing else.

## Stack

- **Language/framework:** FastAPI (Python)
- **Storage:** SQLite, single file, no external DB service
- **Auth:** none
- **Frontend:** none — API only, tested via curl/Postman/the OpenAPI docs page

## Endpoints (this is the entire scope)

| Method | Path | Request body | Behavior | Response |
|---|---|---|---|---|
| `POST` | `/todos` | `{"title": string}` | Create a new todo. `done` defaults to `false`. `id` is auto-generated. | `201`, returns created todo |
| `GET` | `/todos` | — | List all todos. | `200`, returns array of todos |
| `GET` | `/todos/{id}` | — | Get a single todo by id. | `200`, returns todo, or `404` if not found |
| `PUT` | `/todos/{id}` | `{"title"?: string, "done"?: bool}` | Update title and/or done status. Either field optional. | `200`, returns updated todo, or `404` if not found |
| `DELETE` | `/todos/{id}` | — | Delete a todo by id. | `204`, or `404` if not found |
| `PATCH` | `/todos/{id}/toggle` | `Toggle the completion status of a todo` |

## Data Model

Todo:
- `id`: Unique identifier
- `title`: Required string, maximum 200 characters
- `done`: Boolean completion status

### Todo object shape
```json
{
  "id": 1,
  "title": "Buy milk",
  "done": false
}
```

## Explicitly OUT of scope

Do not build any of the following, even if it seems easy to add:

- Authentication or user accounts
- Multi-user support / multi-tenancy
- Pagination, filtering, sorting, or search on `GET /todos`
- Frontend UI of any kind
- Postgres, MySQL, or any external database service
- Docker / Docker Compose / containerization
- Deployment or hosting configuration
- Rate limiting, logging middleware, or observability tooling
- Input validation beyond "title is a non-empty string" and "done is a boolean"

If an agent or teammate suggests any of the above, the answer is "out of scope — later."

## Definition of done

- [ ] `bob plan` run against this file produces a plan covering exactly the 5 endpoints above
- [ ] `bob code` implements the plan
- [ ] Each endpoint has at least one passing happy-path test (edge cases not required)
- [ ] `app/README.md` has a 3-line "how to run this locally" section (install deps, run server, hit an endpoint)
- [ ] `GET /todos` after a `POST` returns the item just created — this is the one manual smoke test everyone should run before calling it done

## Error handling (minimum viable, don't over-engineer)

- `404` with `{"detail": "todo not found"}` for any `{id}` route where the id doesn't exist
- `422` is fine as FastAPI's default for malformed request bodies — no custom validation messages needed