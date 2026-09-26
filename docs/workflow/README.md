# Guarded Multi-Agent Hand-offs

`workflow/handoff_controller.py` turns the original manual sequence into a guarded, auditable hand-off process. It does **not** control or impersonate IBM Bob. A team member still selects the next Bob custom mode, which keeps human approval and IBM Bob's permission boundaries intact.

## What the controller automates

- Checks that the previous stage has produced the evidence required to advance.
- Allows only valid workflow transitions.
- Requires a named human approver for every transition.
- Creates an append-only JSONL audit record in `docs/workflow/handoff-log.jsonl`.
- Prints a hand-off ticket stating the next Bob mode, required inputs, and expected output.
- Generates `docs/workflow/status.md`, a current workflow snapshot.

## Permitted transitions

```text
research → coding → review → testing → docs
                              │
                              └→ debug → coding
```

The `testing → docs` transition requires `PASS` and zero failures in `test_report.md`. The `testing → debug` transition is permitted only when the report records `FAIL`.

## Usage

From the repository root:

```powershell
python workflow/handoff_controller.py status
python workflow/handoff_controller.py handoff review testing --approved-by "Team Member Name"
python workflow/handoff_controller.py handoff testing docs --approved-by "Team Member Name"
```

The controller blocks an invalid transition or missing evidence. After an approved hand-off, select the displayed IBM Bob mode and give it the listed input files.

## Why this is safe

The controller never edits `app/`, never bypasses IBM Bob's file-level permissions, and never claims to run an agent on the team's behalf. It automates the workflow checks and evidence trail while leaving the human approval and actual Bob-mode execution explicit.
