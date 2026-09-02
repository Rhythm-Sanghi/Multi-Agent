# Review Report — app/main.py

**Reviewer:** Review Agent  
**Date:** 2025-07-14  
**Reviewed file:** `app/main.py`  
**Reference documents:** `design_brief.md`, `docs/scope.md` (v2, LOCKED)

---

## Verdict: APPROVED

No blocking issues found. Two informational notes are recorded below for completeness.

---

## Security

### No issues found

All SQL statements use `?` parameterisation for every user-supplied value. No column names or identifiers are interpolated from user input. The previous dynamic `SET` clause in `PUT /todos/{id}` was replaced with three fixed SQL strings in a prior pass — that fix is confirmed in place at lines 156–170.

---

## Scope Violations

### None found

`docs/scope.md` was updated to v2 (LOCKED), explicitly adding `PATCH /todos/{id}/toggle`. The scope violation raised in the previous review report is resolved.

All six endpoints are implemented and match the spec. No routes exist that are not in scope. No forbidden libraries (`sqlalchemy`, `alembic`, etc.) are imported.

| Endpoint | In `docs/scope.md` v2 | Implemented | Match |
|---|---|---|---|
| `POST /todos` | ✅ | ✅ | ✅ |
| `GET /todos` | ✅ | ✅ | ✅ |
| `GET /todos/{id}` | ✅ | ✅ | ✅ |
| `PUT /todos/{id}` | ✅ | ✅ | ✅ |
| `DELETE /todos/{id}` | ✅ | ✅ | ✅ |
| `PATCH /todos/{id}/toggle` | ✅ | ✅ | ✅ |

---

## Code Quality

### [Informational, non-blocking] `_get_conn()` reads `DB_PATH` as a module-level global

**Where:** `app/main.py` lines 73–77

Carried over from the previous review. `_init_db` accepts an optional `path` parameter; `_get_conn` does not and reads the module global directly. Tests work correctly today via `monkeypatch.setattr`. Not blocking — raising for continuity. A consistent fix would be to give `_get_conn` an optional `path` parameter matching `_init_db`.

---

### [Informational, non-blocking] `docs/scope.md` data model names the field `completed`; code uses `done`

**Where:** `docs/scope.md` lines 31–34 (externally modified file)

The v2 `docs/scope.md` data model section lists the completion field as `completed`. The JSON object shape example in the same file (line 41), `design_brief.md`, and the implementation all consistently use `done`. The code is correct. The inconsistency is in the scope document. No code change required — a human should correct `docs/scope.md` line 34 to read `done` instead of `completed`.

---

## Summary

| Category | Blocking | Non-blocking | Informational |
|---|---|---|---|
| Security | 0 | 0 | 0 |
| Scope violations | 0 | 0 | 0 |
| Code quality | 0 | 0 | 2 |

**Overall verdict: APPROVED — no changes required to `app/main.py`.**
