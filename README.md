# Multi-Agent AI Software Team — Built on IBM Bob

A working demonstration of six specialized AI agents collaborating to research, build, review, test, debug, and document a piece of software together — not one AI wearing different hats, but six agents with distinct roles, scoped permissions, and real hand-offs between them.

We're a team of five, built this on [IBM Bob](https://bob.ibm.com), and every claim below is backed by a file in this repo — not just described.

📄 [How we used IBM Bob](IBM_BOB_USAGE.md)

---

## What's actually here

We built a small REST API for a to-do list. The app is deliberately simple — five CRUD endpoints, one small feature added later — because the app was never the point. The point is the pipeline that built it:

```
Research Agent → Coding Agent → Review Agent → Testing Agent → Debug Agent (on failure) → Docs Agent (on pass)
```

Each agent is a custom mode inside IBM Bob, scoped to exactly the files it's allowed to touch. Research Agent can only write `design_brief.md`. Coding Agent can only write inside `app/`. Review Agent can only write `review_report.md`. And so on — nothing here relies on an agent simply choosing to behave; the boundaries are enforced by Bob's permission system.

## Why this exists

Most "AI writes code" demos skip the parts of a real dev process that actually catch mistakes — a second opinion on security, an independent test pass, a real diagnosis when something breaks instead of a guess. We wanted to find out whether a team of narrowly-scoped agents, each handing off to the next, would actually catch things a single-pass approach wouldn't.

We didn't just hope it would. We deliberately broke working code, more than once, to check.

## What it actually caught

- **A real SQL injection pattern**, found by Review Agent in code we'd already shipped and marked passing — column names in a `PUT` handler were being built into a SQL string with an f-string instead of being safely parameterized. See [`review_report.md`](review_report.md).
- **A drifted spec** — our "locked" `docs/scope.md` had quietly fallen out of sync with what we'd actually approved and built. Review Agent caught it; we fixed it and versioned the scope doc.
- **A deliberately introduced bug**, correctly diagnosed by Debug Agent down to the exact two lines responsible — not just a restated error message. See [`debug_report.md`](debug_report.md).
- **The same category of bug, caught independently by CI** — we pushed broken code straight to GitHub Actions and watched it fail automatically, then confirmed it passed again after reverting.

## The six agents

| Agent | Job | Can write to |
|---|---|---|
| Research | Turns a feature request into a concrete design brief | `design_brief.md` only |
| Coding | Implements exactly what the brief specifies | `app/` only |
| Review | Checks for security, scope, and quality issues before testing | `review_report.md` only |
| Testing | Writes and runs tests independently of Coding Agent's own tests | `app/test_*.py`, `test_report.md` |
| Debug | Diagnoses root cause when tests fail, before Coding Agent attempts a fix | `debug_report.md` only |
| Docs | Writes the final README and demo script, only after tests pass | `app/README.md`, `docs/demo-script.md` |

Full agent definitions: [`agent-config/agents/`](agent-config/agents/) (human-readable) and [`.bob/custom_modes.yaml`](.bob/custom_modes.yaml) (what Bob actually runs).

## Repo structure

```
.bob/                    → Bob's real agent config (custom_modes.yaml)
.github/workflows/       → CI: runs the test suite on every push
agent-config/agents/     → Human-readable spec for each of the 6 agents
app/                     → The to-do API itself, tests, and its own README
docs/                    → Locked scope, lessons learned, demo script, run archives
design_brief.md          → Current design brief (Research Agent's output)
review_report.md         → Current review verdict (Review Agent's output)
test_report.md           → Current test results (Testing Agent's output)
debug_report.md          → Most recent failure diagnosis (Debug Agent's output)
```

## Running it yourself

```bash
cd app
pip install -r requirements.txt
uvicorn main:app --reload
```

Full endpoint docs and examples: [`app/README.md`](app/README.md). Interactive API explorer at `http://127.0.0.1:8000/docs` once it's running.

```bash
pytest app/test_main.py -v
```

13 tests, all passing, written independently of the code they test.

## The honest parts

Not everything went smoothly, and we think that's worth saying plainly rather than editing out:

- IBM Bob's own chat interface confidently described a built-in "Orchestrator mode" for auto-chaining agents. It doesn't exist. When we asked Bob to double-check itself, it corrected course. We coordinated agent hand-offs manually instead — which turned out to work reliably across every run, not as a fallback we're apologizing for.
- Testing Agent's write permissions initially blocked it from writing its own `test_report.md` — caught and fixed mid-project.
- A documentation instruction from Docs Agent looked correct but failed on first test, because we ran it from the wrong directory — a reminder to test agent output rather than trust it on sight.

Full account: [`docs/lessons-learned.md`](docs/lessons-learned.md).

## Team

Five of us split ownership across the six agents — research, coding, review & testing, debug & CI, and docs & presentation. Full breakdown in the project report.

---

Built for [problem statement 5: Multi-Agent AI Systems] on IBM Bob.
