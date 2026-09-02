# Debug Report

**Date:** 2025-07-14  
**Triggered by:** `test_report.md` verdict FAIL  
**Debug Agent:** Debug Agent

---

## Failed test

**`test_delete_todo`** — [`app/test_main.py` line 98](app/test_main.py)

```
test_main.py:98: in test_delete_todo
    assert resp.status_code == 204
E   assert 200 == 204
E    +  where 200 = <Response [200 OK]>.status_code
```

---

## Root cause

The `DELETE /todos/{id}` route handler in [`app/main.py`](app/main.py) has the wrong HTTP status code in two places:

**Line 209** — decorator:
```python
@app.delete("/todos/{id}", status_code=status.HTTP_200_OK)
```

**Line 222** — return value:
```python
return Response(status_code=status.HTTP_200_OK)
```

Both should be `status.HTTP_204_NO_CONTENT`. The route executes the DELETE correctly — the SQL runs, the row is removed — but the response it sends back is `200 OK` instead of `204 No Content`.

The test correctly asserts `204` per `design_brief.md`:

> `DELETE /todos/{id}` — `204` (no body), or `404` if not found

There is no ambiguity in the spec. The test is correct. The application code is wrong.

---

## Classification

**APP_BUG**

The spec, the test, and the intent are all consistent. The application code alone is wrong.

---

## Recommended fix location

**File:** [`app/main.py`](app/main.py)  
**Lines:** 209 and 222  
**Change:** Replace both occurrences of `status.HTTP_200_OK` with `status.HTTP_204_NO_CONTENT`. Two-line change, no logic affected.

---

## Confidence

**HIGH** — the failure is a direct status code mismatch between the application and the spec. The error message, the source line, and the spec entry all point to the same two lines with no ambiguity.
