# Demo Script — To-Do REST API

This document is for whoever is presenting or narrating the project. It covers the suggested order for walking through the work, key talking points about the multi-agent pipeline that built it, and specific findings worth calling out.

---

## Suggested narration order

### 1. Start with the running API (30 seconds)

Open a terminal and show the server starting:

```bash
uvicorn app.main:app --reload
```

Then open <http://127.0.0.1:8000/docs> in a browser. The Swagger UI lists all six endpoints. This sets immediate context — the audience can see what was built before hearing how.

---

### 1a. Show the guarded hand-off controller (45 seconds)

Run:

```powershell
python workflow/handoff_controller.py status
python workflow/handoff_controller.py handoff review testing --approved-by "Presenter Name"
```

**Talking point:** The controller does not claim to switch IBM Bob modes itself. It validates the previous stage's evidence, requires a named human approval, records the transition, and prints exactly which Bob mode should run next. This keeps Bob's permission boundaries intact while removing informal hand-off decisions.

For a live presentation, use a real presenter name and keep the generated `docs/workflow/handoff-log.jsonl` as evidence. If an audit log already exists, do not delete it.

---

### 2. Run the smoke test live (1 minute)

Run these two commands in sequence:

```bash
curl -X POST http://127.0.0.1:8000/todos \
  -H "Content-Type: application/json" \
  -d '{"title": "Demo item"}'

curl http://127.0.0.1:8000/todos
```

**Talking point:** The second call returns the item the first call created. This is the single manual verification that matters most — every agent in the pipeline was pointed at this requirement.

---

### 3. Show the test suite passing (1 minute)

```bash
pytest app/test_main.py -v
```

Point out: **23 tests, 0 failures.** Call out the structure:
- One happy-path test per endpoint
- 404 tests for every route that takes an `{id}`
- Title-length validation confirmed on both `POST` and `PUT`
- Missing, blank, and non-string titles rejected with `422`
- Non-boolean `done` values and non-integer route IDs rejected with `422`
- The toggle tested in both directions (false→true→false) in a single test

**Talking point:** Tests run against a throwaway SQLite file created fresh per test using pytest's `tmp_path` fixture. No shared state, no cleanup needed, no mocking.

---

### 4. Walk through the code (2 minutes)

Open `app/main.py`. Point out:

- **Everything is in one file** — schemas, DB helpers, and all six route handlers. Deliberate choice for a project of this size; easy to read top to bottom.
- **`sqlite3` stdlib only** — no ORM, no migration tool, no external DB process. The database file appears on first startup.
- **`done` stored as `INTEGER` 0/1** — SQLite has no native boolean. Pydantic's `TodoOut` schema converts it to `bool` on the way out; callers always see `true`/`false`.
- **`PATCH /todos/{id}/toggle`** — reads the current `done` value in Python and writes back the flipped value. Does not use SQL-level negation (`NOT done`) because that would bypass the Python layer where the conversion lives.

---

### 5. Highlight the review finding that was caught and fixed (2 minutes)

This is the most interesting part of the pipeline story.

**What the review pass caught:** The original `PUT /todos/{id}` implementation built the SQL `SET` clause dynamically using an f-string:

```python
set_clause = ", ".join(f"{col} = ?" for col in fields)
conn.execute(f"UPDATE todos SET {set_clause} WHERE id = ?", values)
```

The values were correctly parameterised, but the column names were interpolated directly. The review flagged this as a latent SQL injection risk: safe today because the keys are hard-coded, but one future edit away from a real vulnerability with no warning in the code.

**How it was fixed:** The dynamic clause was replaced with three fully static SQL strings — one for each combination of fields that can be present (`title` only`, `done` only, both). No identifier interpolation at all.

**Talking point:** This is exactly the kind of subtle issue a human reviewer might also catch on a close read — but the pipeline caught it automatically before anything was merged. The fix is minimal and the behaviour is identical; only the risk surface changed.

---

### 6. Show the second review report (1 minute)

Open `review_report.md` and point to the verdict: **APPROVED.** After the dynamic-SQL fix, the second review pass found zero blocking issues. The historical informational notes are worth mentioning:

- `_get_conn()` originally read the DB path from a module global rather than a parameter; it was subsequently aligned with `_init_db`.
- A scope-document typo (`completed` instead of `done`) was identified and subsequently fixed.

**Talking point:** The review agent correctly distinguished between things that must be fixed before merge and things that are worth noting but don't block. That separation is useful — it avoids the "fix everything or ship nothing" paralysis.

---

## Key talking points — the multi-agent pipeline

| Stage | What happened |
|---|---|
| **Scope** | A locked scope document defined exactly what to build. Every agent was pointed at it. Nothing was added that wasn't in scope. |
| **Design** | A design brief translated the scope into concrete technical decisions: data model, schemas, error handling, library choices. This gave the implementation agent a precise target rather than a vague requirement. |
| **Implementation** | Code was written to the brief exactly — no extras, no "while I'm here" additions. When scope expanded (toggle endpoint), the brief and scope document were updated first, then the code. |
| **Review** | A review pass checked security, scope compliance, and code quality. It caught the SQL injection risk on the first pass and confirmed the fix on the second. |
| **Testing** | Tests were written against the brief, not just against the code that happened to exist. Per-test DB isolation meant no flaky shared state. |
| **Docs** | Documentation was written after PASS — grounded in what was actually built and verified, not what was planned. |

---

## Notable findings worth highlighting

### The dynamic-SQL risk caught in review

The most concrete demonstration of value in the pipeline. The pattern was common dynamic SQL and easy to overlook in review. The review agent flagged it as a latent risk: it was not exploitable in the shipped code because the field names were internally hard-coded, but a future change could have made it unsafe. The fix replaced the dynamic query with fixed SQL statements and did not change behaviour.

### Scope drift was caught before it became permanent

The toggle endpoint was added to the code and the design brief before the locked scope document was updated. The review agent flagged this as a scope violation. Rather than the code quietly drifting from the spec, the discrepancy surfaced immediately and the scope document was updated with explicit team acknowledgment. The pipeline enforced the governance process rather than bypassing it.

### Title validation consistency gap

`TodoCreate` had a non-empty validator on `title`. `TodoUpdate` had the `max_length` constraint but not the non-empty check — meaning `PUT` with `{"title": "   "}` would have written whitespace to the database. The review caught this. A one-paragraph fix aligned the two schemas.

---

## What was deliberately not built

To head off questions: the following were considered and explicitly excluded.

- No pagination on `GET /todos` — a list of all todos is the correct scope for this demo
- No authentication — this is a local-dev API, not a multi-user service  
- No Docker or deployment config — not needed to demonstrate the pipeline
- No ORM — `sqlite3` stdlib is sufficient and keeps the dependency footprint at zero
