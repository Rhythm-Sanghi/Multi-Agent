# Test Report — To-Do REST API

**Testing Agent**  
**Date:** 2025-07-14  
**Branch:** main  
**Test file:** [`app/test_main.py`](app/test_main.py)  
**Application source:** [`app/main.py`](app/main.py)  
**Reference:** [`design_brief.md`](design_brief.md)

---

## Summary

| Metric | Value |
|--------|-------|
| Tests collected | 23 |
| Passed | 23 |
| Failed | 0 |
| Errors | 0 |
| Duration | 0.68 s |

---

## Test Results

| # | Test | Result |
|---|------|--------|
| 1 | `test_create_todo` | ✅ PASS |
| 2 | `test_create_todo_title_too_long` | ✅ PASS |
| 3 | `test_create_todo_title_exactly_200_chars` | ✅ PASS |
| 4 | `test_create_todo_rejects_invalid_title[payload0]` — missing title `{}` | ✅ PASS |
| 5 | `test_create_todo_rejects_invalid_title[payload1]` — whitespace-only title | ✅ PASS |
| 6 | `test_create_todo_rejects_invalid_title[payload2]` — numeric title `123` | ✅ PASS |
| 7 | `test_list_todos` | ✅ PASS |
| 8 | `test_list_todos_empty` | ✅ PASS |
| 9 | `test_get_todo` | ✅ PASS |
| 10 | `test_get_todo_not_found` | ✅ PASS |
| 11 | `test_get_todo_rejects_non_integer_id` | ✅ PASS |
| 12 | `test_update_todo` | ✅ PASS |
| 13 | `test_update_todo_not_found` | ✅ PASS |
| 14 | `test_update_todo_title_too_long` | ✅ PASS |
| 15 | `test_update_todo_rejects_whitespace_title` | ✅ PASS |
| 16 | `test_update_todo_rejects_non_boolean_done` | ✅ PASS |
| 17 | `test_update_todo_empty_body_noop` | ✅ PASS |
| 18 | `test_delete_todo` | ✅ PASS |
| 19 | `test_delete_todo_not_found` | ✅ PASS |
| 20 | `test_delete_todo_double_delete` | ✅ PASS |
| 21 | `test_toggle_todo` (false → true → false) | ✅ PASS |
| 22 | `test_toggle_todo_not_found` | ✅ PASS |
| 23 | `test_post_then_list_returns_item` | ✅ PASS |

---

## Design Brief Coverage

All six endpoints specified in [`design_brief.md`](design_brief.md) are exercised:

| Endpoint | Happy Path | 404 | 422 Validation |
|----------|-----------|-----|----------------|
| `POST /todos` | ✅ | — | ✅ (missing, blank, too-long, non-string title) |
| `GET /todos` | ✅ (empty + populated) | — | — |
| `GET /todos/{id}` | ✅ | ✅ | ✅ (non-integer id) |
| `PUT /todos/{id}` | ✅ (title+done, no-op) | ✅ | ✅ (too-long, blank, non-boolean done) |
| `DELETE /todos/{id}` | ✅ | ✅ (single + double-delete) | — |
| `PATCH /todos/{id}/toggle` | ✅ (both directions) | ✅ | — |

All edge cases from the design brief are covered:

- `POST` with empty/missing/oversized title → `422` ✅
- `PUT` with oversized/blank title → `422` ✅  
- `PUT` with non-boolean `done` → `422` ✅  
- `PUT` with neither field supplied → `200` no-op ✅  
- All mutating operations on non-existent id → `404` with `{"detail": "todo not found"}` ✅  
- `DELETE` returns `204` with no body ✅  
- `done` field is boolean in responses (not `0`/`1`) ✅  
- Non-integer path parameter → `422` ✅  

---

## Warnings

One non-blocking deprecation warning was emitted by `pytest-asyncio` regarding the unset `asyncio_default_fixture_loop_scope` option. This is a third-party plugin configuration issue unrelated to the application under test and does not affect any test results.

---

## Verdict

**PASS — ready to merge.**

All 23 tests passed. Every endpoint, success status code, error status code, and edge case described in `design_brief.md` is covered and behaves correctly.
