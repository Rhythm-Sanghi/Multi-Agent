# Lessons Learned — Multi-Agent To-Do API Build

Running log of friction points, surprises, and deliberate decisions made during
the Research → Coding → Review → Testing pipeline build. Kept honest — includes
things that didn't work, not just successes.

---

## Bob's own chat gave incorrect information about itself

Asked Bob directly whether an "Orchestrator mode" existed for auto-chaining custom
modes. It answered confidently and in detail that Orchestrator mode exists,
including a comparison table of coordination mechanisms. When pushed later, Bob
directly contradicted this, stating Orchestrator mode was never real — only three
built-in modes exist (Agent, Plan, Ask). Lesson: verify AI-provided documentation
against the actual product UI before building a plan around it, even when the
answer is detailed and confident-sounding.

## Testing Agent's write-scope initially blocked its own report

Testing Agent's `fileRegex` was scoped to `app/test_*.py` only, correctly keeping
it from touching application source. But this also blocked it from writing
`test_report.md` at the repo root — an artifact it needed to produce as part of
its job. Fixed by widening the regex to an alternation covering both patterns.
Lesson: scoping an agent's write access requires enumerating every artifact it
needs to produce, not just the source it shouldn't touch.

## Research Agent correctly carried forward context across runs

Across three separate feature-request runs, Research Agent consistently retained
prior constraints (stdlib-only sqlite3, the INTEGER/bool conversion note, the
out-of-scope list) without being re-told each time, and correctly appended new
requirements without disturbing existing ones. This is real evidence the
design-brief-as-persistent-context pattern works, not just a lucky first run.

## Manual mode-switching was the reliable coordination path, not a fallback

Rather than a scripted or auto-orchestrated pipeline, the actual working method
was: switch mode dropdown manually, feed the previous agent's output file to the
next agent's prompt explicitly. This worked reliably across four full pipeline
runs (3 feature requests + 1 retroactive review pass). Worth stating plainly in
the final report rather than treating it as a lesser version of "real" automation.

## Review Agent found a genuine, non-trivial issue on first real use

Run against already-shipped code (retroactive review, not a synthetic test case),
Review Agent flagged:
- A real SQL injection anti-pattern in the PUT handler (column names interpolated
  via f-string, even though today's callers happen to be safe) — fixed
- A real drift between `docs/scope.md` (locked spec) and `design_brief.md` (living
  doc) — the toggle endpoint and title-length validation had been approved and
  built but never reflected back into the original locked scope document
- A real validation gap — PUT allowed whitespace-only titles where POST already
  correctly rejected them — fixed
- One cosmetic inconsistency (`_get_conn`/`_init_db` parameter handling) correctly
  triaged as non-blocking rather than over-flagged

This is meaningfully better evidence than a scripted demo would have produced —
the agent caught something a human reviewer plausibly would have caught too.

## Locked scope documents need a maintenance process, not just an initial lock

`docs/scope.md` was written once at project start and never revisited, even as two
feature requests were deliberately approved and built on top of it. The "LOCKED"
label created a false sense that the document was authoritative when it had
silently drifted. Resolution: amended `docs/scope.md` to v2, explicitly noting the
review-agent finding as the reason for the amendment, rather than either ignoring
the drift or treating every future feature as requiring a from-scratch scope
document.

## Known issue, deliberately deferred (not fixed)

`_get_conn()` reads the module-level `DB_PATH` global directly, while `_init_db()`
accepts an explicit `path` parameter — an asymmetry flagged by Review Agent.
Works correctly today (tests successfully monkeypatch the global), but is a
latent maintenance trap if the two functions' conventions diverge further.
Deliberately deprioritized given the project timeline — documented here rather
than silently dropped, per Review Agent's own non-blocking/blocking distinction.

---

## PowerShell-specific friction (environment, not agent-related)

Worth a brief note since it consumed real time: `curl` in PowerShell is an alias
for `Invoke-WebRequest` with different flag syntax than real curl, multi-line
terminal commands sometimes collapsed onto one line when pasted (breaking
sequential execution), and `Invoke-WebRequest` throws on non-2xx responses rather
than returning them cleanly. None of this reflects on Bob or the agent pipeline —
noted here only because it's a realistic account of what actually slowed
iteration, and worth mentioning briefly in the report as "environment friction,
not agent friction."

Review Agent's addition produced two real fixes (SQL injection pattern, PUT validation gap) and correctly surfaced the scope.md drift as a human decision rather than either ignoring it or trying to resolve it itself. The two-round review cycle (CHANGES REQUESTED → fixes → APPROVED) is good evidence the feedback loop pattern works, not just the linear pipeline.


Debug Agent, tested against a deliberately introduced bug (DELETE returning 200 instead of 204), correctly classified it as APP_BUG, found two separate locations needing the same fix (not just the more obvious one), and gave Coding Agent a precise two-line fix instruction rather than a vague error dump. This is the strongest evidence in the whole project that a dedicated diagnosis step adds real value over just forwarding raw test output.