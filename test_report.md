# Test Report — To-Do REST API

**Date:** 2025-07-14  
**Test file:** `app/test_main.py`  
**Runner:** pytest 9.0.2, Python 3.11.9, Windows  
**Scope reference:** `docs/scope.md` v2 (LOCKED), `design_brief.md`  
**DB isolation:** per-test throwaway SQLite file via `pytest` `tmp_path` + `monkeypatch`

---

## Summary

| Result | Count |
|--------|-------|
| Passed | 13    |
| Failed | 0     |
| Errors | 0     |

---

## Results by endpoint

### `POST /todos`

| Test | Result |
|------|--------|
| `test_create_todo` — returns 201, correct `title`, `done=false`, integer `id` | ✅ PASS |
| `test_create_todo_title_too_long` — title of 201 chars returns 422 | ✅ PASS |

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
| `test_update_todo_title_too_long` — title of 201 chars returns 422 | ✅ PASS |

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

## Coverage against `design_brief.md`

| Requirement | Covered by | Status |
|---|---|---|
| `POST /todos` happy path | `test_create_todo` | ✅ |
| `POST /todos` title max 200 chars | `test_create_todo_title_too_long` | ✅ |
| `GET /todos` happy path | `test_list_todos` | ✅ |
| `GET /todos/{id}` happy path | `test_get_todo` | ✅ |
| `GET /todos/{id}` 404 | `test_get_todo_not_found` | ✅ |
| `PUT /todos/{id}` happy path | `test_update_todo` | ✅ |
| `PUT /todos/{id}` 404 | `test_update_todo_not_found` | ✅ |
| `PUT /todos/{id}` title max 200 chars | `test_update_todo_title_too_long` | ✅ |
| `DELETE /todos/{id}` happy path | `test_delete_todo` | ✅ |
| `DELETE /todos/{id}` 404 | `test_delete_todo_not_found` | ✅ |
| `PATCH /todos/{id}/toggle` happy path (both directions) | `test_toggle_todo` | ✅ |
| `PATCH /todos/{id}/toggle` 404 | `test_toggle_todo_not_found` | ✅ |
| Smoke: `POST` then `GET /todos` returns item | `test_post_then_list_returns_item` | ✅ |

---

## Warnings (non-failing)

- `PendingDeprecationWarning` from `starlette.formparsers`: unrelated to this codebase.
- `PytestDeprecationWarning` from `pytest-asyncio`: no async fixtures in use; no effect.

Neither warning indicates a defect.

---

## Overall verdict

**PASS — ready to merge.**

All 6 endpoints specified in `docs/scope.md` v2 and `design_brief.md` have passing tests. All 404 error paths are covered. Title length validation (≤ 200 chars) is confirmed on both `POST` and `PUT`. The required smoke test passes.
