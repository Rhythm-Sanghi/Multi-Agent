# Test Report — To-Do REST API

**Date:** 2025-07-14  
**Test file:** `app/test_main.py`  
**Runner:** pytest 9.0.2, Python 3.11.9, Windows  
**DB isolation:** per-test throwaway SQLite file via `pytest` `tmp_path` + `monkeypatch`

---

## Summary

| Result | Count |
|--------|-------|
| Passed | 11    |
| Failed | 0     |
| Errors | 0     |

---

## Results by endpoint

### `POST /todos`

| Test | Result |
|------|--------|
| `test_create_todo` — returns 201, correct `title`, `done=false`, integer `id` | ✅ PASS |

### `GET /todos`

| Test | Result |
|------|--------|
| `test_list_todos` — returns 200, array contains the posted item | ✅ PASS |

### `GET /todos/{id}`

| Test | Result |
|------|--------|
| `test_get_todo` — returns 200 and correct data for a known id | ✅ PASS |
| `test_get_todo_not_found` — returns 404 `{"detail": "todo not found"}` for unknown id | ✅ PASS |

### `PUT /todos/{id}`

| Test | Result |
|------|--------|
| `test_update_todo` — returns 200, updated `title` and `done` reflected in response | ✅ PASS |
| `test_update_todo_not_found` — returns 404 `{"detail": "todo not found"}` for unknown id | ✅ PASS |

### `DELETE /todos/{id}`

| Test | Result |
|------|--------|
| `test_delete_todo` — returns 204 for a known id | ✅ PASS |
| `test_delete_todo_not_found` — returns 404 `{"detail": "todo not found"}` for unknown id | ✅ PASS |

### `PATCH /todos/{id}/toggle`

| Test | Result |
|------|--------|
| `test_toggle_todo` — returns 200, `done` flips false→true on first call, true→false on second | ✅ PASS |
| `test_toggle_todo_not_found` — returns 404 `{"detail": "todo not found"}` for unknown id | ✅ PASS |

### Smoke test

| Test | Result |
|------|--------|
| `test_post_then_list_returns_item` — `GET /todos` after `POST` returns the created item | ✅ PASS |

---

## Warnings (non-failing)

- `PendingDeprecationWarning` from `starlette.formparsers`: use `import python_multipart`. Comes from the installed Starlette version; unrelated to this codebase.
- `PytestDeprecationWarning` from `pytest-asyncio`: `asyncio_default_fixture_loop_scope` is unset. This project uses no async fixtures; warning has no effect.

Neither warning indicates a defect.

---

## Overall verdict

**PASS — ready to merge.**

All 6 endpoints (including `PATCH /todos/{id}/toggle`) have passing happy-path tests. All 404 paths are covered. The `POST` → `GET` smoke test required by `docs/scope.md` passes.
