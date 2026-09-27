# Debug Report

## Failed Test(s)

- `test_delete_todo` (`app/test_main.py`, line 139–142)
- `test_delete_todo_double_delete` (`app/test_main.py`, line 151–157) — also asserts `204` on the first delete, so it would fail for the same reason.

---

## Root Cause

The `DELETE /todos/{id}` route in [`app/main.py`](app/main.py) declares its success status code as `HTTP_200_OK` **in two places**:

1. **Route decorator** (line 209):
   ```python
   @app.delete("/todos/{id}", status_code=status.HTTP_200_OK)
   ```
2. **Return value** (line 222):
   ```python
   return Response(status_code=status.HTTP_200_OK)
   ```

Both must be `HTTP_204_NO_CONTENT` (integer `204`). The design brief ([`design_brief.md`](design_brief.md), endpoint table, line 36) explicitly specifies:

> `DELETE /todos/{id}` → success response `204` (no body)

The test ([`app/test_main.py`](app/test_main.py), line 142) correctly asserts `resp.status_code == 204`, which matches the spec exactly.

The application returns `200` instead of `204`, causing the assertion to fail.

---

## Classification

**APP_BUG**

The test is correct and faithful to the design brief. The application code diverges from the spec by using `HTTP_200_OK` where `HTTP_204_NO_CONTENT` is required.

---

## Recommended Fix Location

**File:** [`app/main.py`](app/main.py)

Two targeted changes are needed in the `DELETE /todos/{id}` handler (lines 209 and 222):

1. Change the decorator's `status_code` argument from `status.HTTP_200_OK` to `status.HTTP_204_NO_CONTENT`.
2. Change the explicit `Response(...)` return value's `status_code` argument from `status.HTTP_200_OK` to `status.HTTP_204_NO_CONTENT`.

No other files need to change.

---

## Confidence

**HIGH**

The mismatch is direct and literal — `200` is hardcoded in the app, `204` is required by both the spec and every relevant test assertion. No ambiguity in the evidence.

---

## Resolution Verification

**Original issue:** `DELETE /todos/{id}` in [`app/main.py`](app/main.py) returned HTTP `200 OK` instead of the `204 No Content` required by [`design_brief.md`](design_brief.md) and asserted by the tests.

**Fix applied:** Two references to `status.HTTP_200_OK` in the `DELETE /todos/{id}` handler were changed to `status.HTTP_204_NO_CONTENT`:

| Location | Before | After |
|---|---|---|
| Route decorator (line 209) | `status_code=status.HTTP_200_OK` | `status_code=status.HTTP_204_NO_CONTENT` |
| Return statement (line 222) | `Response(status_code=status.HTTP_200_OK)` | `Response(status_code=status.HTTP_204_NO_CONTENT)` |

**Verification status:** All three DELETE-related tests now pass — `test_delete_todo`, `test_delete_todo_not_found`, and `test_delete_todo_double_delete`. The full test suite (23 tests) passes with zero failures and zero regressions.

**Final classification:** RESOLVED APP_BUG

**Scope:** No unrelated code was modified. The fix is confined to the two `HTTP_200_OK` tokens in the DELETE handler; all other endpoints, schemas, and helpers are unchanged.
