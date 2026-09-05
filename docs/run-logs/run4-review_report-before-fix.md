# Review Report — app/main.py

**Reviewer:** Review Agent
**Date:** 2025-07-14
**Reviewed file:** `app/main.py`
**Reference documents:** `design_brief.md`, `docs/scope.md`

---

## Verdict: CHANGES REQUESTED

Two blocking issues found. Two non-blocking notes recorded for the Coding Agent's awareness.

---

## Blocking Issues (2)

### 1. Security — SQL injection risk in `PUT /todos/{id}`

**Where:** `app/main.py:150`

Column names from `fields.keys()` are interpolated directly into the SQL string using an f-string. The values themselves are safely parameterised, but the column names are not. Today the keys are hard-coded to `"title"` and `"done"` and cannot come from user input — but there is no enforcement of that invariant in the code. The pattern is a latent injection vector that one future edit could activate.

**Recommended fix:** Use an explicit allowlist before interpolating, or replace the dynamic `SET` clause with fixed, static `UPDATE` statements for each combination of fields that can be present.

---

### 2. Scope violation — `PATCH /todos/{id}/toggle` not in `docs/scope.md`

**Where:** `app/main.py:171–188`

`docs/scope.md` is marked LOCKED and lists exactly five endpoints. The toggle endpoint was added to `design_brief.md` but `docs/scope.md` was never updated to reflect it.

**Recommendation:** This needs explicit team agreement on `docs/scope.md` before the route can be considered formally in-scope. This is a human decision, not something the Coding Agent should resolve on its own.

---

## Non-blocking Notes (2)

### 3. Quality — `TodoUpdate.title` missing non-empty validator

**Where:** `app/main.py:31–33`

`design_brief.md` specifies that the non-empty constraint on `title` applies when it's supplied on `PUT` as well as `POST`. Currently, a `PUT` with `{"title": "   "}` passes validation when it should be rejected.

---

### 4. Quality — `_get_conn()` is inconsistent with `_init_db()`

**Where:** `app/main.py:66–70`

`_init_db` accepts an optional `path` parameter; `_get_conn` reads the module-level `DB_PATH` global directly instead. Works correctly today via `monkeypatch` in tests, but the asymmetry is a latent maintenance trap if the two functions' calling conventions diverge further.

---

## Summary

| Category | Blocking | Non-blocking |
|---|---|---|
| Security | 1 | 0 |
| Scope violations | 1 | 0 |
| Code quality | 0 | 2 |

**Overall verdict: CHANGES REQUESTED — 2 blocking issues must be resolved before this can be approved.**