# Demonstrate the workflow

Run commands from the repository root after installing `app/requirements.txt`
in an isolated environment. Use disposable demo data for API writes.

## Suggested flow

1. Start `python -m uvicorn app.main:app --reload` and open
   http://127.0.0.1:8000/docs. Create/list a to-do item to show the API.
2. Open `.bob/custom_modes.yaml` and the role definitions. Explain the edit-path
   rules and separate read/execute permissions.
3. Run `python workflow/handoff_controller.py status`. This checks existing
   evidence and writes a status snapshot; it does not run agents.
4. Show `review_report.md` and `debug_report.md`. Distinguish the risky SQL pattern
   from an exploitable issue, and the deliberate DELETE bug from a production incident.
5. Run `python -m pytest app/test_main.py workflow/test_handoff_controller.py -v`.
   Present the actual result for the current revision rather than a hardcoded count.
6. Show the hand-off JSONL log. Explain that mode selection and approval are human
   actions and a recorded name is not an authenticated enterprise identity.

Only demonstrate a hand-off with `--approved-by` when a real team member approves
that transition. Preserve previous log entries; do not manufacture or clear evidence.

## Static walkthrough

`judge-dashboard/index.html` is an authored static page. Serve it with
`python -m http.server 8080 --directory judge-dashboard`. Its animation replays
recorded steps and does not execute agents, CI or pytest. Recorded pass counts
are historical; use the live test command to check a new revision.

## Scope to explain

The API is a small local demonstration with no authentication or production
infrastructure. The workflow adds review/test/diagnosis roles but still depends
on human judgment and the recorded scope. Production use would need authenticated
approvals, operational controls and deployment-specific validation.
