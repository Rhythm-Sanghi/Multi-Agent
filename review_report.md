# Review Report — app/main.py

**Reviewer:** Review Agent  
**Date:** 2025-07-14  
**Reviewed file:** `app/main.py`  
**Reference documents:** `design_brief.md`, `docs/scope.md`

---

## Verdict: CHANGES REQUESTED

One blocking security issue must be fixed before this is mergeable. Two non-blocking quality notes are also raised.

---

## Security Findings

### [BLOCKING] SQL injection via dynamic column name interpolation in `PUT /todos/{id}`

**Where:** [`app/main.py` line 150](app/main.py)

```python
set_clause = ", ".join(f"{col} = ?" for col in fields)
...
conn.execute(f"UPDATE todos SET {set_clause} WHERE id = ?", values)
```

**Severity:** High

**What:** The column names in `set_clause` are built by interpolating `col` directly into the SQL string using an f-string. The values themselves are correctly parameterised (`?`), but the column names are not. SQLite does not support parameterised identifiers, so this pattern is the standard approach — **however**, `fields` is populated from `payload.title` and `payload.done` by name, meaning the keys are always the literal strings `"title"` and `"done"` sourced from the handler's own code, not from user input.

**Why it is still a finding:** The safety of this pattern is entirely implicit — it depends on the reader knowing that `fields.keys()` can only ever be `"title"` or `"done"` because the two `if` blocks above it hard-code those key names. There is no enforcement of that invariant in the code itself. A future contributor adding a new field to `TodoUpdate` and appending it to `fields` with a key derived from user input (e.g., iterating `payload.model_fields`) would silently introduce a real injection vector with no indication that column names are being interpolated unsafely.

**Fix:** Replace the open-ended dictionary accumulation with an explicit allowlist of column names. For example:

```python
ALLOWED_COLUMNS = {"title", "done"}
# ... build fields only from known keys, assert membership before interpolation
```

Or, since there are only two possible fields, use two separate fixed UPDATE statements selected by which fields are present, eliminating interpolation entirely.

---

## Scope Violations

### [BLOCKING] `PATCH /todos/{id}/toggle` is not in `docs/scope.md`

**Where:** [`app/main.py` lines 171–188](app/main.py)

**What:** `docs/scope.md` is explicitly marked **LOCKED** and defines exactly five endpoints. The `PATCH /todos/{id}/toggle` endpoint is not among them. `design_brief.md` has been updated to include it, but `docs/scope.md` — the stated single source of truth — has not, and explicitly says: *"If an agent or teammate suggests any of the above, the answer is 'out of scope — later.'"*

**Severity:** Blocking — this is a scope governance issue, not a code quality issue.

**Action required:** Either (a) get explicit team agreement to update `docs/scope.md` to add the toggle endpoint and uncheck the relevant Definition of Done items, or (b) remove the `PATCH /todos/{id}/toggle` route until that agreement is in place. The Coding Agent should not decide this — it requires a human decision.

---

## Code Quality Notes

### [Non-blocking] `TodoUpdate` does not enforce non-empty on `title` when supplied

**Where:** [`app/main.py` lines 31–33](app/main.py)

**What:** `TodoCreate` correctly rejects an empty or whitespace-only `title` via `title_not_empty`. `TodoUpdate.title` has `max_length=200` via `Field` but no equivalent non-empty validator. `design_brief.md` states: *"If `title` is supplied, same constraints apply: non-empty and ≤ 200 characters."* A `PUT` request with `{"title": "   "}` would pass validation and write whitespace to the database.

**Severity:** Non-blocking — the brief specifies this constraint; the implementation does not fully honour it. Does not affect correctness of the happy path but diverges from the spec.

---

### [Non-blocking] `_get_conn()` reads `DB_PATH` as a module-level global, not a parameter

**Where:** [`app/main.py` lines 66–70](app/main.py)

```python
def _get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
```

**What:** `_init_db` correctly accepts `path` as a parameter, making it straightforward to override in tests. `_get_conn` does not — it reads the module-level `DB_PATH` directly. The test fixture works around this with `monkeypatch.setattr(main_module, "DB_PATH", ...)`, which patches the global before the connection is opened. This is functional but fragile: if `_get_conn` were ever called before the monkeypatch runs (e.g., at import time), it would silently use the production DB. The inconsistency between the two helpers is also confusing.

**Severity:** Non-blocking — tests pass today. Worth making `_get_conn` consistent with `_init_db` by accepting an optional `path` parameter.
