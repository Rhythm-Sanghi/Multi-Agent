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
| Passed | 17    |
| Failed | 0     |
| Errors | 0     |

---

## Results by endpoint

### `POST /todos`

| Test | Expected | Actual | Result |
|------|----------|--------|--------|
| `test_create_todo` — happy path | 201, correct fields | 201 ✓ | ✅ PASS |
| `test_create_todo_title_too_long` — 201-char title | 422 | 422 ✓ | ✅ PASS |
| `test_create_todo_title_exactly_200_chars` *(new)* — title at 200-char boundary | 201, title preserved | 201 ✓ | ✅ PASS |

### `GET /todos`

| Test | Expected | Actual | Result |
|------|----------|--------|--------|
| `test_list_todos` — one item present | 200, array with item | 200 ✓ | ✅ PASS |
| `test_list_todos_empty` *(new)* — empty table | 200, `[]` | 200, `[]` ✓ | ✅ PASS |

### `GET /todos/{id}`

| Test | Expected | Actual | Result |
|------|----------|--------|--------|
| `test_get_todo` — known id | 200, correct data | 200 ✓ | ✅ PASS |
| `test_get_todo_not_found` — unknown id | 404 `{"detail": "todo not found"}` | 404 ✓ | ✅ PASS |

### `PUT /todos/{id}`

| Test | Expected | Actual | Result |
|------|----------|--------|--------|
| `test_update_todo` — update both fields | 200, updated fields | 200 ✓ | ✅ PASS |
| `test_update_todo_not_found` — unknown id | 404 `{"detail": "todo not found"}` | 404 ✓ | ✅ PASS |
| `test_update_todo_title_too_long` — 201-char title | 422 | 422 ✓ | ✅ PASS |
| `test_update_todo_empty_body_noop` *(new)* — empty body `{}` | 200, unchanged todo | 200, unchanged ✓ | ✅ PASS |

### `DELETE /todos/{id}`

| Test | Expected | Actual | Result |
|------|----------|--------|--------|
| `test_delete_todo` — known id | 204 | 204 ✓ | ✅ PASS |
| `test_delete_todo_not_found` — unknown id | 404 `{"detail": "todo not found"}` | 404 ✓ | ✅ PASS |
| `test_delete_todo_double_delete` *(new)* — delete same id twice | first: 204, second: 404 | 204 then 404 ✓ | ✅ PASS |

### `PATCH /todos/{id}/toggle`

| Test | Expected | Actual | Result |
|------|----------|--------|--------|
| `test_toggle_todo` — toggle both directions | 200, false→true→false | 200 ✓ | ✅ PASS |
| `test_toggle_todo_not_found` — unknown id | 404 `{"detail": "todo not found"}` | 404 ✓ | ✅ PASS |

### Smoke test

| Test | Expected | Actual | Result |
|------|----------|--------|--------|
| `test_post_then_list_returns_item` — POST then GET | item appears in list | ✓ | ✅ PASS |

---

## New edge-case tests added this run

| Test | Scenario | spec reference |
|------|----------|----------------|
| `test_create_todo_title_exactly_200_chars` | Title at the exact 200-char boundary must succeed | `design_brief.md` — `title`: max 200 characters |
| `test_list_todos_empty` | `GET /todos` on an empty table returns `200` with `[]`, not an error | `design_brief.md` — `GET /todos`: returns array |
| `test_update_todo_empty_body_noop` | `PUT` with `{}` is a no-op returning `200` with unchanged data | `design_brief.md` — neither field required; "no fields change… return 200" |
| `test_delete_todo_double_delete` | Second DELETE on the same id returns `404` | `design_brief.md` — `DELETE`: `404` if not found |

No application code changes were required. All four new tests passed against the existing implementation.

---

## Coverage against `design_brief.md`

| Requirement | Covered by | Status |
|---|---|---|
| `POST /todos` happy path | `test_create_todo` | ✅ |
| `POST /todos` title exactly 200 chars | `test_create_todo_title_exactly_200_chars` | ✅ |
| `POST /todos` title > 200 chars → 422 | `test_create_todo_title_too_long` | ✅ |
| `GET /todos` happy path | `test_list_todos` | ✅ |
| `GET /todos` empty table → `[]` | `test_list_todos_empty` | ✅ |
| `GET /todos/{id}` happy path | `test_get_todo` | ✅ |
| `GET /todos/{id}` 404 | `test_get_todo_not_found` | ✅ |
| `PUT /todos/{id}` happy path | `test_update_todo` | ✅ |
| `PUT /todos/{id}` empty body no-op → 200 | `test_update_todo_empty_body_noop` | ✅ |
| `PUT /todos/{id}` 404 | `test_update_todo_not_found` | ✅ |
| `PUT /todos/{id}` title > 200 chars → 422 | `test_update_todo_title_too_long` | ✅ |
| `DELETE /todos/{id}` happy path | `test_delete_todo` | ✅ |
| `DELETE /todos/{id}` 404 | `test_delete_todo_not_found` | ✅ |
| `DELETE /todos/{id}` double-delete → 404 | `test_delete_todo_double_delete` | ✅ |
| `PATCH /todos/{id}/toggle` both directions | `test_toggle_todo` | ✅ |
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

All 6 endpoints pass. 4 new edge-case tests added (title at 200-char boundary, empty GET, no-op PUT with `{}`, double-DELETE), all passing. No application code changes required.
